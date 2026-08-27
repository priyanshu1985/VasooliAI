import React from 'react';

/**
 * Reusable stat card (label, value, optional delta/subtext).
 */
export default function MetricCard({ label, value, subtext, delta, icon: Icon, color = "blue" }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex flex-col justify-between">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-slate-500">{label}</span>
        {Icon && <Icon className="w-5 h-5 text-slate-400" />}
      </div>
      <div className="mt-4 flex items-baseline gap-2">
        <span className="text-3xl font-bold text-slate-900">{value}</span>
        {delta && (
          <span className="text-sm font-semibold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full">
            {delta}
          </span>
        )}
      </div>
      {subtext && <p className="mt-2 text-xs text-slate-400">{subtext}</p>}
    </div>
  );
}
