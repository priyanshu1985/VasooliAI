"""
combine_data.py

Combines REAL transaction structure (amounts, timing patterns) from a public
Kaggle dataset with SYNTHETIC, Faker-generated labels for the things no public
dataset provides: subscription decline reasons and retry outcomes.

Why hybrid: no public dataset exists with subscription-failure decline-reason
+ retry-outcome labels (that's proprietary business data). Grounding our
amount/time distributions in a real dataset makes the data look and behave
like real money movement, while the synthetic labels give us controllable
ground truth to honestly measure model accuracy against.

If --kaggle_csv is not found, this script falls back to a realistic synthetic
distribution (lognormal amounts, realistic hour-of-day weighting) so you can
keep developing without the real file. Swap in the real CSV before your final
training run for the strongest, most honest story.
"""

import argparse
import numpy as np
import pandas as pd
from faker import Faker
import os

fake = Faker()
Faker.seed(42)
np.random.seed(42)

# Consolidated into 4 ACTIONABLE categories rather than raw bank codes.
# Design decision: many raw bank decline codes (bank_do_not_honor, bank_timeout,
# otp_auth_failure) all lead to the exact same downstream action — "retry
# later" — and are not meaningfully separable from structured features alone
# (real payment systems bucket them the same way for this reason). Keeping
# them split made the classification problem artificially fragmented without
# adding any real decision-making value. These 4 categories are what actually
# drives a different recovery action, which is what Stage 2 needs anyway.
DECLINE_REASONS = {
    "insufficient_funds_or_technical": 0.55,  # soft decline -> retry later
    "card_expired": 0.22,                     # needs card update, not a blind retry
    "risk_fraud_flag": 0.23,                  # hard decline (incl. lost/stolen) -> manual review, never retry
}

SOFT_DECLINE = {"insufficient_funds_or_technical"}
HARD_DECLINE = {"risk_fraud_flag"}
CARD_ISSUE = {"card_expired"}


def load_real_distribution(kaggle_csv_path: str, n_records: int):
    """Pull realistic amount + hour-of-day distributions from the real Kaggle CSV
    if present; otherwise fall back to a realistic synthetic distribution."""
    if kaggle_csv_path and os.path.exists(kaggle_csv_path):
        print(f"[combine_data] Loading REAL distribution from {kaggle_csv_path}")
        df = pd.read_csv(kaggle_csv_path, nrows=200_000)
        amt_col = "amt" if "amt" in df.columns else df.select_dtypes("number").columns[0]
        amounts = df[amt_col].dropna().values
        amounts = amounts[(amounts > 0) & (amounts < 5000)]  # keep to subscription-realistic range
        if "trans_date_trans_time" in df.columns:
            hours = pd.to_datetime(df["trans_date_trans_time"], errors="coerce").dt.hour.dropna().values
        else:
            hours = np.random.choice(range(24), size=len(amounts))
        sampled_amounts = np.random.choice(amounts, size=n_records, replace=True)
        sampled_hours = np.random.choice(hours, size=n_records, replace=True)
        return sampled_amounts, sampled_hours, True
    else:
        print("[combine_data] Kaggle CSV not found — using realistic synthetic fallback. "
              "Swap in the real file before your final run (see ml/README.md).")
        # Mixture distribution: most are small monthly subscriptions, a minority
        # are larger annual/premium plans — this realistic spread is what makes
        # an amount-based fraud-risk threshold actually reachable and meaningful.
        is_annual = np.random.rand(n_records) < 0.15
        monthly = np.random.lognormal(mean=3.1, sigma=0.5, size=n_records)
        annual = np.random.lognormal(mean=6.0, sigma=0.4, size=n_records)
        sampled_amounts = np.where(is_annual, annual, monthly)
        sampled_amounts = np.round(np.clip(sampled_amounts, 5, 3000), 2)
        # realistic hour weighting: fewer attempts at 2-5am, more 9am-9pm
        hour_weights = np.array([1,1,1,1,1,2,3,4,5,6,6,6,6,6,6,6,6,6,5,5,4,3,2,1])
        sampled_hours = np.random.choice(range(24), size=n_records, p=hour_weights/hour_weights.sum())
        return sampled_amounts, sampled_hours, False


def assign_reason(amount, hour, past_failure_count, subscription_age_days) -> str:
    """Assigns a decline reason using clear rule-based archetypes plus realistic
    noise — this mirrors how real-world decline reasons genuinely correlate with
    these signals (fraud checks skew toward odd hours/high amounts, expired
    cards skew toward old subscriptions, insufficient funds skews toward repeat
    failures). A mild multiplier on the base rates was too weak a signal for a
    model to learn from; this priority-rule design gives it real structure
    while still keeping enough randomness to stay honest, not artificially perfect."""
    r = np.random.rand()
    is_odd_hour = (hour < 7)

    # Priority 1: fraud/risk signature — unusual hour combined with a high amount
    # (threshold calibrated to sit above typical monthly amounts, within reach
    # of the annual/premium-plan tail of the distribution). Kept as a genuine
    # minority class (fraud SHOULD be rare) but widened enough to be learnable
    # rather than reduced to a handful of unusable examples.
    if is_odd_hour and amount > 100:
        if r < 0.85:
            return "risk_fraud_flag"
        else:
            return "insufficient_funds_or_technical"

    # Priority 2: old subscription -> card likely expired
    if subscription_age_days > 500:
        if r < 0.80:
            return "card_expired"
        else:
            return "insufficient_funds_or_technical"

    # Priority 3: repeat-failure customer -> soft decline (funds/technical)
    if past_failure_count >= 2:
        if r < 0.85:
            return "insufficient_funds_or_technical"
        else:
            return "card_expired"

    # Default / baseline case
    if r < 0.80:
        return "insufficient_funds_or_technical"
    elif r < 0.93:
        return "card_expired"
    else:
        return "risk_fraud_flag"


def generate_dataset(n_records: int, kaggle_csv_path: str) -> pd.DataFrame:
    amounts, hours, used_real = load_real_distribution(kaggle_csv_path, n_records)

    rows = []
    for i in range(n_records):
        amount = float(amounts[i])
        hour = int(hours[i])
        day_of_week = np.random.randint(0, 7)  # 0=Mon
        retry_count_so_far = np.random.choice([0, 1, 2], p=[0.6, 0.3, 0.1])
        past_failure_count = np.random.poisson(0.8)
        subscription_age_days = np.random.randint(1, 900)

        # Reason is now CAUSED BY the features above, not independent of them —
        # this is what gives the model real, learnable, honest signal.
        reason = assign_reason(amount, hour, past_failure_count, subscription_age_days)

        is_retriable = reason in SOFT_DECLINE  # ground truth business rule for realism

        rows.append({
            "payment_id": f"PAY{i:05d}",
            "customer_name": fake.name(),
            "amount": round(amount, 2),
            "hour_of_day": hour,
            "day_of_week": day_of_week,
            "retry_count_so_far": retry_count_so_far,
            "past_failure_count": past_failure_count,
            "subscription_age_days": subscription_age_days,
            "decline_reason_true": reason,          # HIDDEN ground truth for evaluation
            "is_soft_decline_true": reason in SOFT_DECLINE,
            "is_retriable_true": is_retriable,
        })

    df = pd.DataFrame(rows)
    df.attrs["used_real_kaggle_distribution"] = used_real
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--kaggle_csv", type=str, default="data/kaggle_raw/fraudTrain.csv")
    parser.add_argument("--n_records", type=int, default=300)
    parser.add_argument("--out", type=str, default="data/failed_payments.csv")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    df = generate_dataset(args.n_records, args.kaggle_csv)
    df.to_csv(args.out, index=False)

    print(f"[combine_data] Wrote {len(df)} records to {args.out}")
    print(f"[combine_data] Used real Kaggle distribution: {df.attrs['used_real_kaggle_distribution']}")
    print(df["decline_reason_true"].value_counts())
