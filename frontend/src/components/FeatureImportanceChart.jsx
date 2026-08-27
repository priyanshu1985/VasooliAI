import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

/**
 * Horizontal bar chart for ML Feature Importance ranking.
 */
export default function FeatureImportanceChart({ data = [], takeaway }) {
  const sortedData = [...data].sort((a, b) => a.importance - b.importance);

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <h3 className="text-lg font-semibold text-slate-800 mb-2">Stage 1 — Feature Importance</h3>
      <p className="text-xs text-slate-500 mb-4">Relative importance assigned by the trained Random Forest classifier</p>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            layout="vertical"
            data={sortedData}
            margin={{ top: 10, right: 30, left: 80, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e8f0" />
            <XAxis type="number" stroke="#64748b" domain={[0, 'dataMax + 0.05']} />
            <YAxis
              type="category"
              dataKey="feature"
              stroke="#64748b"
              tick={{ fontSize: 12 }}
            />
            <Tooltip
              formatter={(value) => [`${(value * 100).toFixed(1)}%`, 'Importance']}
              contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #e2e8f0' }}
            />
            <Bar dataKey="importance" fill="#4f46e5" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {takeaway && (
        <p className="mt-4 text-sm font-medium text-slate-600 border-t border-slate-100 pt-3">
          💡 <span className="text-slate-800 font-semibold">Key takeaway:</span> {takeaway}
        </p>
      )}
    </div>
  );
}
