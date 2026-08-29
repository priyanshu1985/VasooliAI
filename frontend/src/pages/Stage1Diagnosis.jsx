import React, { useEffect, useState } from 'react';
import ConfusionMatrix from '../components/ConfusionMatrix';
import FeatureImportanceChart from '../components/FeatureImportanceChart';
import { getStage1Metrics } from '../api/client';

export default function Stage1Diagnosis() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchMetrics = () => {
    setLoading(true);
    setError(null);
    getStage1Metrics()
      .then(setData)
      .catch((err) => {
        console.error('Failed to load stage 1 metrics:', err);
        setError('Unable to load Stage 1 metrics from server.');
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  if (loading && !data) {
    return (
      <div className="p-12 text-center text-slate-500 flex flex-col items-center justify-center">
        <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mb-4" />
        <p className="text-sm font-medium">Evaluating Stage 1 Random Forest model metrics...</p>
      </div>
    );
  }

  if (error && !data) {
    return (
      <div className="p-8 bg-red-50 border border-red-200 rounded-xl text-center text-red-700">
        <p className="font-semibold mb-2">{error}</p>
        <button
          onClick={fetchMetrics}
          className="mt-2 px-4 py-2 bg-red-600 text-white rounded-lg text-xs font-semibold hover:bg-red-700 transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  const { labels, confusion_matrix, feature_importance, takeaway, accuracy } = data || {};

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Stage 1 — Failed-Subscription Recovery (Diagnosis)</h2>
          <p className="text-sm text-slate-500 mt-1">
            Random Forest multi-class classifier predicting failure root cause from structured metadata only (no LLM).
          </p>
        </div>
        {accuracy && (
          <div className="bg-indigo-50 border border-indigo-200 px-4 py-2 rounded-xl text-xs font-semibold text-indigo-900">
            Held-out Test Accuracy: <span className="text-indigo-600 font-bold text-sm">{accuracy}%</span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <ConfusionMatrix labels={labels} matrix={confusion_matrix} takeaway={takeaway} />
        <FeatureImportanceChart data={feature_importance} takeaway={takeaway} />
      </div>
    </div>
  );
}
