import React, { useEffect, useState } from 'react';
import EscalationFunnel from '../components/EscalationFunnel';
import AuditTrailTable from '../components/AuditTrailTable';
import AuditQuestionBox from '../components/AuditQuestionBox';
import MetricCard from '../components/MetricCard';
import VoiceRecoverySimulator from '../components/VoiceRecoverySimulator';
import { getStage3Metrics, getAuditTrail, extractPromiseLive } from '../api/client';

export default function Stage3PromiseAudit() {
  const [stage3Data, setStage3Data] = useState(null);
  const [auditData, setAuditData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Interactive Live Gemini Promise Tester state
  const [testInput, setTestInput] = useState('I was traveling, will definitely pay the INR 4500 invoice this Friday, 2026-09-04.');
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);

  useEffect(() => {
    Promise.all([getStage3Metrics(), getAuditTrail()])
      .then(([s3, audit]) => {
        setStage3Data(s3);
        setAuditData(audit);
      })
      .catch((err) => console.error('Failed to load stage 3/audit data:', err))
      .finally(() => setLoading(false));
  }, []);

  const handleTestExtraction = async (e) => {
    e.preventDefault();
    if (!testInput.trim()) return;
    try {
      setTesting(true);
      const res = await extractPromiseLive(testInput);
      setTestResult(res);
    } catch (err) {
      console.error('Failed to extract promise:', err);
    } finally {
      setTesting(false);
    }
  };

  if (loading) {
    return (
      <div className="p-12 text-center text-slate-500 flex flex-col items-center justify-center">
        <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mb-4" />
        <p className="text-sm font-medium">Loading Stage 3 & live Supabase audit trail...</p>
      </div>
    );
  }

  const { promises_kept, promises_broken, promise_kept_rate, escalation_funnel, takeaway } = stage3Data || {};
  const { rows, total_count } = auditData || {};

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-xl font-bold text-slate-900">Stage 3 — Promise-to-Pay Tracker & Audit Trail</h2>
        <p className="text-sm text-slate-500 mt-1">
          Google Gemini LLM promise extraction paired with Yale-study calibrated escalation and 100% audit trail coverage on Supabase PostgreSQL.
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
          subtext="100% decision traceability on Supabase"
        />
      </div>

      {/* Live Interactive Gemini Promise Tester */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
              Live Interactive Gemini LLM Promise Extractor
            </h3>
            <p className="text-xs text-slate-500">
              Test real-time natural language commitment extraction against Google Gemini API (gemini-3.6-flash)
            </p>
          </div>
        </div>

        <form onSubmit={handleTestExtraction} className="space-y-4">
          <div className="flex gap-3">
            <input
              type="text"
              value={testInput}
              onChange={(e) => setTestInput(e.target.value)}
              placeholder="e.g. Will pay 2500 by Monday once salary credits"
              className="flex-1 text-xs sm:text-sm bg-slate-50 border border-slate-300 rounded-lg px-4 py-2.5 text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <button
              type="submit"
              disabled={testing}
              className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-60 text-white rounded-lg text-xs font-semibold shadow-xs transition-colors flex items-center gap-2 whitespace-nowrap"
            >
              {testing ? (
                <>
                  <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Extracting...
                </>
              ) : (
                'Extract Promise (Gemini)'
              )}
            </button>
          </div>
        </form>

        {testResult && (
          <div className="mt-4 p-4 bg-slate-50 rounded-lg border border-slate-200 text-xs space-y-2">
            <div className="flex flex-wrap gap-4 items-center">
              <span className="font-semibold text-slate-800">Extraction Output:</span>
              <span
                className={`px-2 py-0.5 rounded-full font-semibold ${
                  testResult.is_promise
                    ? 'bg-emerald-100 text-emerald-800'
                    : 'bg-slate-200 text-slate-700'
                }`}
              >
                {testResult.is_promise ? '✓ Promise Commitment Detected' : '✗ No Promise Detected'}
              </span>
              {testResult.promised_date && (
                <span className="bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded font-mono font-medium">
                  Date: {testResult.promised_date}
                </span>
              )}
              {testResult.promised_amount && (
                <span className="bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded font-mono font-medium">
                  Amount: ₹{testResult.promised_amount}
                </span>
              )}
              <span className="text-slate-500">
                Confidence: <strong className="text-slate-800">{(testResult.confidence * 100).toFixed(0)}%</strong>
              </span>
            </div>
            <p className="text-slate-600 italic">
              <strong>Reasoning:</strong> {testResult.reasoning}
            </p>
          </div>
        )}
      </div>

      {/* Stage 4 — Hinglish Voice Recovery Simulator */}
      <VoiceRecoverySimulator paymentId="pay_demo_unresponsive_89" />

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

      {/* Feature 2: Ask Your Audit Trail a Question */}
      <AuditQuestionBox />

      <AuditTrailTable rows={rows} totalCount={total_count} />
    </div>
  );
}
