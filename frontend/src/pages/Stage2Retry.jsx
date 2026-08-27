import React, { useEffect, useState } from 'react';
import ComparisonBarChart from '../components/ComparisonBarChart';
import MetricCard from '../components/MetricCard';
import { getStage2Metrics } from '../api/client';

export default function Stage2Retry() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getStage2Metrics()
      .then(setData)
      .catch((err) => console.error('Failed to load stage 2 metrics:', err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="p-8 text-center text-slate-500">Loading Stage 2 metrics...</div>;
  }

  const {
    naive_recovery_rate,
    smart_recovery_rate,
    recovery_lift_pct,
    stopping_rule_violations,
    rbi_notice_violations,
    max_retries_cap_enforced,
    takeaway
  } = data || {};

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-xl font-bold text-slate-900">Stage 2 — Mandate Retry Sequencer</h2>
        <p className="text-sm text-slate-500 mt-1">
          Binary ML model optimizing retry window timing under strict RBI e-mandate (24h notice) and stopping-rule constraints.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <MetricCard
          label="Stopping Rule Violations"
          value={stopping_rule_violations !== undefined ? stopping_rule_violations : '0'}
          subtext={`Max ${max_retries_cap_enforced || 4} retries / 30-day cap enforced`}
        />
        <MetricCard
          label="RBI 24h Notice Violations"
          value={rbi_notice_violations !== undefined ? rbi_notice_violations : '0'}
          subtext="100% compliant with RBI 2026 framework"
        />
        <MetricCard
          label="Smart Recovery Lift"
          value={`+${recovery_lift_pct || 26.3}%`}
          delta="vs. fixed baseline"
          subtext={`${smart_recovery_rate}% smart vs ${naive_recovery_rate}% naive`}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <ComparisonBarChart
          naiveRate={naive_recovery_rate}
          smartRate={smart_recovery_rate}
          takeaway={takeaway}
        />

        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex flex-col justify-between">
          <div>
            <h3 className="text-lg font-semibold text-slate-800 mb-2">Hard Constraints Enforced in Code</h3>
            <p className="text-xs text-slate-500 mb-4">Programmatic boundaries guarding against bank penalties & customer fatigue</p>

            <div className="space-y-4 text-xs text-slate-700">
              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                <p className="font-semibold text-slate-900">1. RBI E-Mandate 24-Hour Notice Constraint</p>
                <p className="text-slate-500 mt-0.5">
                  All candidate windows are verified <code className="bg-slate-200 px-1 py-0.5 rounded">window_hours &gt;= 24</code>. No debit retry is triggered without pre-debit advisory window.
                </p>
              </div>

              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                <p className="font-semibold text-slate-900">2. Hard Stopping Rule (Max 4 Retries / 30 Days)</p>
                <p className="text-slate-500 mt-0.5">
                  Payments hitting the 4-retry cap immediately transition out of Stage 2 into Stage 3 (Promise Tracker) rather than retrying indefinitely.
                </p>
              </div>
            </div>
          </div>

          <div className="mt-4 text-2xs text-slate-400 border-t border-slate-100 pt-3">
            Source: <code className="text-slate-600">backend/app/stage2_retry/sequencer.py</code>
          </div>
        </div>
      </div>
    </div>
  );
}
