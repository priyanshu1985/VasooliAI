import React, { useState } from 'react';
import { askAuditTrail } from '../api/client';

export default function AuditQuestionBox({ onQuerySuccess }) {
  const [question, setQuestion] = useState('');
  const [paymentIdFilter, setPaymentIdFilter] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const sampleQuestions = [
    "Why was payment PAY00007 stopped or scheduled?",
    "What were the most common Stage 1 root cause diagnoses?",
    "Why did Stage 2 pause reminders or schedule retries?",
    "How many customer commitments were extracted in Stage 3?"
  ];

  const handleAsk = async (e) => {
    if (e) e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const res = await askAuditTrail({
        question: question.trim(),
        payment_id: paymentIdFilter.trim() || undefined,
      });
      setResult(res);
      if (onQuerySuccess) onQuerySuccess(res);
    } catch (err) {
      console.error("Audit QA error:", err);
      setError("Failed to query audit trail. Please check connection and try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-base font-semibold text-slate-800">Ask Your Audit Trail a Question</span>
            <span className="text-2xs bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded font-mono font-medium">
              Gemini LLM
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Ask plain-English questions about logged recovery decisions, rule violations, and outcomes.
          </p>
        </div>
      </div>

      <form onSubmit={handleAsk} className="space-y-3">
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
          <div className="sm:col-span-3">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="e.g. Why did Stage 2 schedule a retry in +72h instead of +24h?"
              className="w-full text-xs px-3.5 py-2.5 bg-slate-50 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white"
            />
          </div>
          <div>
            <input
              type="text"
              value={paymentIdFilter}
              onChange={(e) => setPaymentIdFilter(e.target.value)}
              placeholder="Filter Payment ID (optional)"
              className="w-full text-xs px-3.5 py-2.5 bg-slate-50 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white font-mono"
            />
          </div>
        </div>

        {/* Quick Suggestion Chips */}
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="text-2xs text-slate-400 font-medium mr-1">Quick prompts:</span>
          {sampleQuestions.map((sq, i) => (
            <button
              key={i}
              type="button"
              onClick={() => setQuestion(sq)}
              className="text-2xs bg-slate-100 hover:bg-indigo-50 hover:text-indigo-700 text-slate-600 px-2.5 py-1 rounded-md transition-colors"
            >
              {sq}
            </button>
          ))}
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={loading || !question.trim()}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-lg text-xs font-semibold shadow-xs transition-colors flex items-center gap-2"
          >
            {loading ? (
              <>
                <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Analyzing Audit Logs...
              </>
            ) : (
              <>
                <span>💬</span> Ask Audit Trail
              </>
            )}
          </button>
        </div>
      </form>

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-xs text-red-700">
          {error}
        </div>
      )}

      {result && (
        <div className="mt-4 p-4 bg-slate-50 border border-indigo-100 rounded-xl space-y-2">
          <div className="flex items-center justify-between text-2xs text-slate-500">
            <span className="font-semibold text-indigo-900">Decision Audit Synthesis</span>
            <span>
              Analyzed <strong>{result.rows_analyzed}</strong> log rows · Model: <code className="text-slate-700 font-mono">{result.model_used || 'gemini'}</code>
            </span>
          </div>
          <div className="text-xs text-slate-800 leading-relaxed bg-white p-3 rounded-lg border border-slate-200">
            {result.answer}
          </div>
        </div>
      )}
    </div>
  );
}
