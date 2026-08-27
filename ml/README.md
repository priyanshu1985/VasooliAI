# ML Pipeline — Data Combination + Training

## Step 0 — External setup required (cannot be done automatically)

1. Create a free Kaggle account at https://www.kaggle.com if you don't have one.
2. Install the Kaggle CLI and set up your API token:
   ```bash
   pip install kaggle --break-system-packages
   # Go to kaggle.com -> your profile -> Settings -> API -> "Create New Token"
   # This downloads kaggle.json — place it at ~/.kaggle/kaggle.json
   chmod 600 ~/.kaggle/kaggle.json
   ```
3. Download the recommended dataset (simulated but realistic large-scale transaction data — merchant, amount, timestamp, category fields):
   ```bash
   kaggle datasets download -d kartik2112/fraud-detection
   unzip fraud-detection.zip -d data/kaggle_raw
   ```
   This gives you `fraudTrain.csv` — we only use its **realistic amount and timestamp distributions**, not its fraud labels (our project needs decline-reason and retry-outcome labels instead, which don't exist publicly, so we generate those ourselves — see combine_data.py).

4. If you don't have the Kaggle file yet, `combine_data.py` automatically falls back to a realistic synthetic distribution so you can keep developing — just swap in the real CSV path later before your final training run.

## Step 1 — Run the data combination script
```bash
python combine_data.py --kaggle_csv data/kaggle_raw/fraudTrain.csv --n_records 300 --out data/failed_payments.csv
```

## Step 2 — Train Stage 1 (Diagnosis classifier)
Open and run all cells in `notebooks/02_stage1_diagnosis_training.ipynb` (via Jupyter Lab/Notebook, or VS Code's notebook interface).

Outputs: `outputs/stage1_confusion_matrix.png`, `outputs/stage1_feature_importance.png`, printed accuracy/precision/recall report, and the trained model saved to `models/stage1_diagnosis_model.pkl`.

## Step 3 — Train Stage 2 (Retry sequencer model)
Open and run all cells in `notebooks/03_stage2_retry_training.ipynb`.

Outputs: printed naive-vs-smart recovery rate comparison, `outputs/stage2_comparison.png`, and the trained model saved to `models/stage2_retry_model.pkl`.

## Why notebooks for training
Notebooks let you inspect the dataframe, rerun a single cell after tweaking a hyperparameter, and see each chart render immediately below the cell that made it — this is the right tool for the *exploration and training* phase. The **saved `.pkl` model files** in `models/` are what actually get used afterward — the FastAPI backend loads these directly rather than retraining live. See `docs/architecture.md` section 7 for the full reasoning.

## Files in this folder
- `combine_data.py` — merges real Kaggle-derived distributions with Faker-generated synthetic labels (stays a plain script — a single linear pass, not something explored interactively)
- `notebooks/02_stage1_diagnosis_training.ipynb` — feature engineering, train/test split, classifier training, evaluation, model saving
- `notebooks/03_stage2_retry_training.ipynb` — candidate-window expansion, model training, naive-vs-smart comparison, model saving
- `models/` — the trained `.pkl` files the backend loads at runtime
- `outputs/` — generated charts (gitignored)
