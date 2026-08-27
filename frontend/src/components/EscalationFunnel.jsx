import React from 'react';

/**
 * Stacked visual representation of the Stage 3 Escalation Ladder funnel.
 */
export default function EscalationFunnel({ funnel = {}, takeaway }) {
  const steps = [
    { key: 'gentle_reminder', label: 'Gentle Reminder (Text)', color: 'bg-emerald-500', count: funnel.gentle_reminder || 0 },
    { key: 'firmer_nudge', label: 'Firmer Nudge (+48h)', color: 'bg-amber-500', count: funnel.firmer_nudge || 0 },
    { key: 'final_notice', label: 'Final Notice (Impending cancellation)', color: 'bg-orange-500', count: funnel.final_notice || 0 },
    { key: 'stopped', label: 'Outreach Stopped (Hard cap)', color: 'bg-slate-400', count: funnel.stopped || 0 },
  ];

  const maxCount = Math.max(...steps.map(s => s.count), 1);

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <h3 className="text-lg font-semibold text-slate-800 mb-2">Stage 3 — Escalation Ladder</h3>
      <p className="text-xs text-slate-500 mb-4">Graduated contact frequency respecting harassment limits and Yale study findings</p>

      <div className="space-y-3">
        {steps.map((step) => {
          const widthPct = Math.max(12, Math.round((step.count / maxCount) * 100));
          return (
            <div key={step.key} className="space-y-1">
              <div className="flex justify-between text-xs font-medium text-slate-700">
                <span>{step.label}</span>
                <span className="font-semibold text-slate-900">{step.count} attempts</span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden">
                <div
                  className={`h-full ${step.color} rounded-full transition-all duration-300`}
                  style={{ width: `${widthPct}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {takeaway && (
        <p className="mt-4 text-sm font-medium text-slate-600 border-t border-slate-100 pt-3">
          💡 <span className="text-slate-800 font-semibold">Key takeaway:</span> {takeaway}
        </p>
      )}
    </div>
  );
}
