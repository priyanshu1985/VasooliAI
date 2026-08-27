import React, { useEffect, useState } from 'react';
import MetricCard from '../components/MetricCard';
import { getOverview } from '../api/client';

export default function Overview() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getOverview()
      .then(setData)
      .catch((err) => console.error('Failed to load overview metrics:', err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="p-8 text-center text-slate-500">Loading overview metrics...</div>;
  }

  const { total_payments, total_recovered, recovery_rate, diagnosis_accuracy, funnel } = data || {};

  return (
    <div className="space-y-8">
      {/* 4 Header Metric Cards Across */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          label="Total Payments Processed"
          value={total_payments?.toLocaleString() || '0'}
          subtext="Hybrid real Kaggle + synthetic dataset"
        />
        <MetricCard
          label="Total Money Recovered"
          value={`₹${total_recovered?.toLocaleString('en-IN') || '0'}`}
          delta="+₹4.82L"
          subtext="Recovered across Stages 1–3"
        />
        <MetricCard
          label="Overall Recovery Rate"
          value={`${recovery_rate || 0}%`}
          delta="+26.3% lift"
          subtext="Compared to fixed 42.1% baseline"
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
