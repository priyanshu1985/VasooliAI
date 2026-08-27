import React, { useEffect, useState } from 'react';
import ConfusionMatrix from '../components/ConfusionMatrix';
import FeatureImportanceChart from '../components/FeatureImportanceChart';
import { getStage1Metrics } from '../api/client';

export default function Stage1Diagnosis() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getStage1Metrics()
      .then(setData)
      .catch((err) => console.error('Failed to load stage 1 metrics:', err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="p-8 text-center text-slate-500">Loading Stage 1 metrics...</div>;
  }

  const { labels, confusion_matrix, feature_importance, takeaway } = data || {};

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-xl font-bold text-slate-900">Stage 1 — Failed-Subscription Recovery (Diagnosis)</h2>
        <p className="text-sm text-slate-500 mt-1">
          Random Forest multi-class classifier predicting failure root cause from structured metadata only (no LLM).
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <ConfusionMatrix labels={labels} matrix={confusion_matrix} takeaway={takeaway} />
        <FeatureImportanceChart data={feature_importance} takeaway={takeaway} />
      </div>
    </div>
  );
}
