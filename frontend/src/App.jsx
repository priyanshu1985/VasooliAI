import React, { useState } from 'react';
import NavBar from './components/NavBar';
import Overview from './pages/Overview';
import Stage1Diagnosis from './pages/Stage1Diagnosis';
import Stage2Retry from './pages/Stage2Retry';
import Stage3PromiseAudit from './pages/Stage3PromiseAudit';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      <NavBar activeTab={activeTab} setActiveTab={setActiveTab} />
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' && <Overview />}
        {activeTab === 'stage1' && <Stage1Diagnosis />}
        {activeTab === 'stage2' && <Stage2Retry />}
        {activeTab === 'stage3' && <Stage3PromiseAudit />}
      </main>
      <footer className="border-t border-slate-200 bg-white py-4 text-center text-xs text-slate-400">
        AI Revenue Recovery Agent · Track: AI Revenue Recovery · Razorpay AI Buildathon 2026
      </footer>
    </div>
  );
}
