import React from 'react';

/**
 * Top navigation bar across the 4 dashboard views.
 */
export default function NavBar({ activeTab, setActiveTab }) {
  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'stage1', label: 'Stage 1: Diagnosis' },
    { id: 'stage2', label: 'Stage 2: Retry Sequencer' },
    { id: 'stage3', label: 'Stage 3: Promise & Audit' },
  ];

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-10 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold text-lg shadow-sm">
              ₹
            </div>
            <div>
              <h1 className="text-base font-bold text-slate-900 leading-tight">AI Revenue Recovery Agent</h1>
              <p className="text-2xs text-slate-500 font-medium">Razorpay AI Buildathon 2026</p>
            </div>
          </div>
          <nav className="flex space-x-1 sm:space-x-4">
            {tabs.map((tab) => {
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-3 py-2 rounded-lg text-xs sm:text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-indigo-50 text-indigo-700 font-semibold'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`}
                >
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>
      </div>
    </header>
  );
}
