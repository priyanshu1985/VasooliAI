import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts';

/**
 * Reusable side-by-side comparison bar chart (e.g. Naive vs Smart Recovery).
 */
export default function ComparisonBarChart({ naiveRate = 42.1, smartRate = 68.4, takeaway }) {
  const data = [
    {
      name: 'Recovery Rate (%)',
      'Naive Fixed-Schedule': naiveRate,
      'Smart Model-Picked': smartRate,
    },
  ];

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <h3 className="text-lg font-semibold text-slate-800 mb-4">Naive vs. Smart Retry Recovery</h3>
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
            <XAxis dataKey="name" stroke="#64748b" />
            <YAxis unit="%" stroke="#64748b" domain={[0, 100]} />
            <Tooltip
              formatter={(value) => [`${value}%`]}
              contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #e2e8f0' }}
            />
            <Legend />
            <Bar dataKey="Naive Fixed-Schedule" fill="#94a3b8" radius={[4, 4, 0, 0]} />
            <Bar dataKey="Smart Model-Picked" fill="#10b981" radius={[4, 4, 0, 0]} />
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
