import React from 'react';

/**
 * Grid-based confusion matrix component with color intensity heat mapping.
 */
export default function ConfusionMatrix({ labels = [], matrix = [], takeaway }) {
  // Find maximum cell value for dynamic intensity normalization
  const maxVal = matrix.reduce((max, row) => Math.max(max, ...row), 1);

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 overflow-x-auto">
      <h3 className="text-lg font-semibold text-slate-800 mb-2">Stage 1 — Confusion Matrix</h3>
      <p className="text-xs text-slate-500 mb-4">Predicted class (horizontal) vs. Ground Truth class (vertical)</p>

      <div className="inline-block min-w-full">
        <table className="border-collapse text-xs">
          <thead>
            <tr>
              <th className="p-2 border-b border-slate-200 text-left font-medium text-slate-400">Actual \ Predicted</th>
              {labels.map((label, idx) => (
                <th key={idx} className="p-2 border-b border-slate-200 font-medium text-slate-700 text-center capitalize">
                  {label.replace(/_/g, ' ')}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {matrix.map((row, rIdx) => (
              <tr key={rIdx}>
                <td className="p-2 border-r border-slate-200 font-medium text-slate-700 capitalize whitespace-nowrap">
                  {labels[rIdx]?.replace(/_/g, ' ') || `Class ${rIdx}`}
                </td>
                {row.map((cell, cIdx) => {
                  const intensity = Math.min(1, cell / maxVal);
                  const isDiagonal = rIdx === cIdx;
                  return (
                    <td
                      key={cIdx}
                      className={`p-3 text-center font-semibold border border-slate-100 ${
                        isDiagonal
                          ? 'bg-indigo-600 text-white'
                          : cell > 0
                          ? 'bg-indigo-50 text-indigo-900'
                          : 'bg-slate-50 text-slate-400'
                      }`}
                      style={{
                        backgroundColor: isDiagonal
                          ? `rgba(79, 70, 229, ${0.4 + intensity * 0.6})`
                          : cell > 0
                          ? `rgba(239, 68, 68, ${0.1 + intensity * 0.3})`
                          : undefined
                      }}
                    >
                      {cell}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {takeaway && (
        <p className="mt-4 text-sm font-medium text-slate-600 border-t border-slate-100 pt-3">
          💡 <span className="text-slate-800 font-semibold">Key takeaway:</span> {takeaway}
        </p>
      )}
    </div>
  );
}
