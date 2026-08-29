import React, { useState } from 'react';

/**
 * Searchable, sortable, and filterable Audit Trail table component.
 */
export default function AuditTrailTable({ rows = [], totalCount = 0 }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [stageFilter, setStageFilter] = useState('all');

  const filteredRows = rows.filter((row) => {
    const matchesSearch =
      row.payment_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      row.decision?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      row.reasoning?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStage = stageFilter === 'all' || row.stage === stageFilter;
    return matchesSearch && matchesStage;
  });

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
      <div className="p-6 border-b border-slate-200 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold text-slate-800">Immutable Audit Trail</h3>
          <p className="text-xs text-slate-500">Every decision, rule validation, and outcome logged across all 3 stages</p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={stageFilter}
            onChange={(e) => setStageFilter(e.target.value)}
            className="text-xs bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="all">All Stages</option>
            <option value="stage1">Stage 1 (Diagnose)</option>
            <option value="stage2">Stage 2 (Retry)</option>
            <option value="stage3">Stage 3 (Promise)</option>
          </select>
          <input
            type="text"
            placeholder="Search payment ID, reason..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="text-xs bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-700 w-48 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-600">
          <thead className="bg-slate-50 text-slate-700 font-semibold border-b border-slate-200">
            <tr>
              <th className="py-3 px-4">Timestamp</th>
              <th className="py-3 px-4">Stage</th>
              <th className="py-3 px-4">Payment ID</th>
              <th className="py-3 px-4">Decision Taken</th>
              <th className="py-3 px-4">Reasoning / Model Input</th>
              <th className="py-3 px-4">Outcome</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {filteredRows.length > 0 ? (
              filteredRows.map((row, idx) => (
                <tr key={idx} className="hover:bg-slate-50 transition-colors">
                  <td className="py-3 px-4 font-mono text-slate-400 whitespace-nowrap">
                    {new Date(row.timestamp).toLocaleTimeString()}
                  </td>
                  <td className="py-3 px-4 whitespace-nowrap">
                    <span
                      className={`inline-flex items-center px-2 py-0.5 rounded-full text-2xs font-semibold ${
                        row.stage === 'stage1'
                          ? 'bg-blue-100 text-blue-800'
                          : row.stage === 'stage2'
                          ? 'bg-emerald-100 text-emerald-800'
                          : 'bg-purple-100 text-purple-800'
                      }`}
                    >
                      {row.stage?.toUpperCase()}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-mono font-medium text-slate-900 whitespace-nowrap">
                    <div className="flex items-center gap-1.5">
                      <span>{row.payment_id}</span>
                      {row.reasoning?.includes('razorpay_webhook') && (
                        <span className="inline-flex items-center px-1.5 py-0.2 rounded text-2xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
                          Razorpay Live
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="py-3 px-4 font-medium text-slate-800">{row.decision}</td>
                  <td className="py-3 px-4 text-slate-500 max-w-xs truncate">{row.reasoning}</td>
                  <td className="py-3 px-4 whitespace-nowrap">
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-2xs font-medium bg-slate-100 text-slate-700">
                      {row.outcome}
                    </span>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={6} className="py-6 text-center text-slate-400">
                  No matching audit records found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
