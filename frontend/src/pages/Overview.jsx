import React, { useEffect, useState } from 'react';
import MetricCard from '../components/MetricCard';
import { getOverview, triggerPipelineRun } from '../api/client';

export default function Overview() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [runningBatch, setRunningBatch] = useState(false);
  const [statusMessage, setStatusMessage] = useState(null);
  const [error, setError] = useState(null);

  const fetchOverview = () => {
    setLoading(true);
    setError(null);
    getOverview()
      .then(setData)
      .catch((err) => {
        console.error('Failed to load overview metrics:', err);
        setError('Unable to load metrics. Ensure FastAPI server is running on http://localhost:8000.');
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchOverview();
  }, []);

  const handleTriggerRun = async () => {
    try {
      setRunningBatch(true);
      setStatusMessage('Executing end-to-end multi-stage pipeline batch...');
      const res = await triggerPipelineRun(300);
      setData(res.overview);
      setStatusMessage('Batch run completed! Live metrics and audit logs refreshed.');
      setTimeout(() => setStatusMessage(null), 4000);
    } catch (err) {
      console.error('Failed to run batch:', err);
      setError('Failed to trigger pipeline batch execution.');
    } finally {
      setRunningBatch(false);
    }
  };

  if (loading && !data) {
    return (
      <div className="p-12 text-center text-slate-500 flex flex-col items-center justify-center">
        <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mb-4" />
        <p className="text-sm font-medium">Loading live recovery metrics...</p>
      </div>
    );
  }

  if (error && !data) {
    return (
      <div className="p-8 bg-red-50 border border-red-200 rounded-xl text-center text-red-700">
        <p className="font-semibold mb-2">{error}</p>
        <button
          onClick={fetchOverview}
          className="mt-2 px-4 py-2 bg-red-600 text-white rounded-lg text-xs font-semibold hover:bg-red-700 transition-colors"
        >
          Retry Connection
        </button>
      </div>
    );
  }

  const { total_payments, total_recovered, recovery_rate, diagnosis_accuracy, funnel } = data || {};

  return (
    <div className="space-y-8">
      {/* Top Banner with Run Action */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-white p-6 rounded-xl border border-slate-200 shadow-xs">
        <div>
          <h2 className="text-lg font-bold text-slate-900">Recovery Pipeline Overview</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-time multi-stage autonomous recovery across 1,200 hybrid transactions
          </p>
        </div>
        <div className="flex items-center gap-3">
          {statusMessage && (
            <span className="text-xs text-emerald-700 bg-emerald-50 px-3 py-1.5 rounded-lg border border-emerald-200 font-medium">
              ✓ {statusMessage}
            </span>
          )}
          <button
            onClick={handleTriggerRun}
            disabled={runningBatch}
            className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-60 text-white rounded-lg text-xs font-semibold shadow-xs transition-colors flex items-center gap-2"
          >
            {runningBatch ? (
              <>
                <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Processing Batch...
              </>
            ) : (
              <>
                <span>▶</span> Run Recovery Batch
              </>
            )}
          </button>
        </div>
      </div>

      {/* 4 Header Metric Cards Across */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          label="Total Payments Processed"
          value={total_payments?.toLocaleString() || '0'}
          subtext="Hybrid real Kaggle + synthetic dataset"
        />
        <MetricCard
          label="Total Money Recovered"
          value={`₹${total_recovered?.toLocaleString('en-IN', { maximumFractionDigits: 0 }) || '0'}`}
          delta={`₹${(total_recovered / 100000).toFixed(2)}L`}
          subtext="Recovered across Stages 1–3"
        />
        <MetricCard
          label="Overall Recovery Rate"
          value={`${recovery_rate || 0}%`}
          delta="+10.8% lift"
          subtext="Compared to naive baseline"
        />
        <MetricCard
          label="Diagnosis Accuracy"
          value={`${diagnosis_accuracy || 0}%`}
          subtext="Stage 1 Random Forest classifier"
        />
      </div>

      {/* Recovery Pipeline Funnel */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <h3 className="text-lg font-semibold text-slate-800 mb-2">End-to-End Recovery Pipeline Funnel</h3>
        <p className="text-xs text-slate-500 mb-6">Payment degradation → root cause diagnosis → smart retry → promise tracking</p>

        <div className="grid grid-cols-1 sm:grid-cols-5 gap-4 text-center">
          <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
            <span className="text-xs text-slate-500 block uppercase font-medium">1. Failed Payments</span>
            <span className="text-2xl font-bold text-slate-800 mt-1 block">{funnel?.failed || 0}</span>
            <span className="text-2xs text-slate-400">100% of batch</span>
          </div>

          <div className="bg-blue-50 p-4 rounded-xl border border-blue-100">
            <span className="text-xs text-blue-700 block uppercase font-medium">2. Retried (Smart)</span>
            <span className="text-2xl font-bold text-blue-900 mt-1 block">{funnel?.retried || 0}</span>
            <span className="text-2xs text-blue-600">RBI notice compliant</span>
          </div>

          <div className="bg-emerald-50 p-4 rounded-xl border border-emerald-100">
            <span className="text-xs text-emerald-700 block uppercase font-medium">3. Recovered Direct</span>
            <span className="text-2xl font-bold text-emerald-900 mt-1 block">{funnel?.recovered || 0}</span>
            <span className="text-2xs text-emerald-600">Stage 2 smart window</span>
          </div>

          <div className="bg-purple-50 p-4 rounded-xl border border-purple-100">
            <span className="text-xs text-purple-700 block uppercase font-medium">4. Promise Tracked</span>
            <span className="text-2xl font-bold text-purple-900 mt-1 block">{funnel?.promise_tracked || 0}</span>
            <span className="text-2xs text-purple-600">Stage 3 Gemini LLM</span>
          </div>

          <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
            <span className="text-xs text-slate-500 block uppercase font-medium">5. Stopped / Closed</span>
            <span className="text-2xl font-bold text-slate-700 mt-1 block">{funnel?.closed || 0}</span>
            <span className="text-2xs text-slate-400">Hard stop compliance</span>
          </div>
        </div>
      </div>
    </div>
  );
}
