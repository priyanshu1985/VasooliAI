import React, { useEffect, useState } from 'react';
import EscalationFunnel from '../components/EscalationFunnel';
import AuditTrailTable from '../components/AuditTrailTable';
import MetricCard from '../components/MetricCard';
import { getStage3Metrics, getAuditTrail } from '../api/client';

export default function Stage3PromiseAudit() {
  const [stage3Data, setStage3Data] = useState(null);
  const [auditData, setAuditData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getStage3Metrics(), getAuditTrail()])
      .then(([s3, audit]) => {
        setStage3Data(s3);
        setAuditData(audit);
      })
      .catch((err) => console.error('Failed to load stage 3/audit data:', err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="p-8 text-center text-slate-500">Loading Stage 3 & Audit Trail...</div>;
  }

  const { promises_kept, promises_broken, promise_kept_rate, escalation_funnel, takeaway } = stage3Data || {};
  const { rows, total_count } = auditData || {};

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-xl font-bold text-slate-900">Stage 3 — Promise-to-Pay Tracker & Audit Trail</h2>
        <p className="text-sm text-slate-500 mt-1">
          Google Gemini LLM promise extraction paired with Yale-study calibrated escalation and 100% audit trail coverage.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <MetricCard
          label="Promises Kept"
          value={promises_kept || 0}
          delta={`${promise_kept_rate || 0}% kept`}
          subtext="Commitments fulfilled on promised date"
        />
        <MetricCard
          label="Promises Broken"
          value={promises_broken || 0}
          subtext="Triggered graduated escalation ladder"
        />
        <MetricCard
          label="Audit Trail Rows"
          value={total_count || rows?.length || 0}
          subtext="100% decision traceability"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <EscalationFunnel funnel={escalation_funnel} takeaway={takeaway} />

        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex flex-col justify-between">
          <div>
            <h3 className="text-lg font-semibold text-slate-800 mb-2">Yale Study Research Grounding</h3>
            <p className="text-xs text-slate-500 mb-4">Why Stage 3 uses a stricter follow-up cadence</p>
            <div className="p-3 bg-amber-50 rounded-lg border border-amber-200 text-xs text-amber-900 space-y-2">
              <p className="font-semibold">Empirical Finding (Prof. James Choi, Yale):</p>
              <p>
                AI-solicited promises are broken more often than human commitments, recovering ~9% less in the first 30 days if left unmonitored.
              </p>
              <p className="text-amber-800 font-medium">
                Our design incorporates an accelerated check-in on the exact promised date and bounded escalation to close this gap.
              </p>
            </div>
          </div>
          <div className="mt-4 text-2xs text-slate-400 border-t border-slate-100 pt-3">
            Source: <code className="text-slate-600">docs/architecture.md §3</code>
          </div>
        </div>
      </div>

      <AuditTrailTable rows={rows} totalCount={total_count} />
    </div>
  );
}
