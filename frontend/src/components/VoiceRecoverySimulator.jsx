import React, { useState } from 'react';

export default function VoiceRecoverySimulator({ paymentId = 'pay_demo_unresponsive_89' }) {
  const [calling, setCalling] = useState(false);
  const [callActive, setCallActive] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [speechError, setSpeechError] = useState(null);

  const HINGLISH_SCRIPT =
    'Namaste! Aapka payment fail ho gaya hai. Kya aap Friday tak pay kar sakte hain? Haan ke liye 1 dabayein, Nahi ke liye 2.';

  const handleStartCall = () => {
    setResult(null);
    setSpeechError(null);
    setCalling(true);

    if (!('speechSynthesis' in window)) {
      setSpeechError('Browser Web Speech API not supported. Displaying Hinglish transcript below.');
      setCalling(false);
      setCallActive(true);
      return;
    }

    try {
      window.speechSynthesis.cancel(); // Stop any pending speech
      const utterance = new SpeechSynthesisUtterance(HINGLISH_SCRIPT);
      
      // Auto-detect Hindi voice or fallback to Indian English/default
      const voices = window.speechSynthesis.getVoices();
      const hindiVoice = voices.find((v) => v.lang.includes('hi') || v.lang.includes('IN'));
      if (hindiVoice) {
        utterance.voice = hindiVoice;
        utterance.lang = 'hi-IN';
      } else {
        utterance.lang = 'en-IN';
      }

      utterance.rate = 0.95; // Natural conversational pace

      utterance.onend = () => {
        setCalling(false);
        setCallActive(true);
      };

      utterance.onerror = () => {
        setCalling(false);
        setCallActive(true);
      };

      window.speechSynthesis.speak(utterance);
    } catch (err) {
      setSpeechError('Audio playback issue; transcript displayed on screen.');
      setCalling(false);
      setCallActive(true);
    }
  };

  const handleKeyPress = async (key) => {
    try {
      setSubmitting(true);
      const res = await fetch('http://localhost:8000/api/stage4/voice-response', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ payment_id: paymentId, keypress: key }),
      });
      const data = await res.json();
      setResult(data);
      setCallActive(false);
    } catch (err) {
      console.error('Failed to submit voice response:', err);
      setResult({
        status: 'error',
        decision: 'Could not connect to backend server on localhost:8000.',
      });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-xs border border-slate-200 p-6 space-y-5">
      {/* Header & Trigger Condition Notice */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-4">
        <div>
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <span>📞</span> Stage 4 — Hinglish Voice Recovery Simulator
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            IVR Voice Escalation for customers unresponsive after 2+ SMS/WhatsApp outreach attempts.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[11px] font-semibold px-2.5 py-1 rounded-full bg-amber-50 text-amber-700 border border-amber-200">
            Target: {paymentId} (Unresponsive)
          </span>
        </div>
      </div>

      {/* Main Action Banner */}
      <div className="bg-slate-50 rounded-lg p-4 border border-slate-200/80 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="space-y-1">
          <p className="text-xs font-semibold text-slate-800">Trigger Autonomous Voice Call</p>
          <p className="text-xs text-slate-500">
            Uses Web Speech API TTS in Hindi/Indian accent + on-screen transcript.
          </p>
        </div>
        <button
          onClick={handleStartCall}
          disabled={calling || submitting}
          className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-60 text-white rounded-lg text-xs font-semibold shadow-xs transition-colors flex items-center gap-2 shrink-0"
        >
          {calling ? (
            <>
              <div className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Agent Speaking Out Loud...
            </>
          ) : (
            <>
              <span>🔊</span> Simulate Hinglish Voice Call
            </>
          )}
        </button>
      </div>

      {speechError && (
        <p className="text-xs text-amber-700 bg-amber-50 p-2.5 rounded border border-amber-200">
          ⚠️ {speechError}
        </p>
      )}

      {/* Live Transcript / Subtitles Box */}
      {(calling || callActive || result) && (
        <div className="bg-slate-900 text-slate-100 p-4 rounded-lg space-y-2 text-xs">
          <div className="flex items-center justify-between text-slate-400 border-b border-slate-800 pb-1.5">
            <span className="flex items-center gap-1.5">
              <span className={`w-2 h-2 rounded-full ${calling ? 'bg-emerald-400 animate-ping' : 'bg-slate-500'}`} />
              Agent Audio Transcript (Hinglish):
            </span>
            <span className="text-[10px] text-slate-500">hi-IN / en-IN TTS</span>
          </div>
          <p className="italic text-emerald-300 font-mono text-sm leading-relaxed">
            "{HINGLISH_SCRIPT}"
          </p>
        </div>
      )}

      {/* Simulated Phone Keypad Response Buttons */}
      {callActive && (
        <div className="p-4 bg-indigo-50/60 border border-indigo-100 rounded-lg space-y-3">
          <p className="text-xs font-bold text-indigo-950">
            Customer Phone Keypad Response (Simulated):
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <button
              onClick={() => handleKeyPress(1)}
              disabled={submitting}
              className="p-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold text-left transition-colors flex items-center justify-between shadow-xs"
            >
              <div>
                <span className="font-bold text-sm block">1 — Haan, pay karunga</span>
                <span className="text-[10px] text-emerald-100">Commitment to pay by Friday</span>
              </div>
              <span className="text-lg">✓</span>
            </button>

            <button
              onClick={() => handleKeyPress(2)}
              disabled={submitting}
              className="p-3 bg-rose-600 hover:bg-rose-700 text-white rounded-lg text-xs font-semibold text-left transition-colors flex items-center justify-between shadow-xs"
            >
              <div>
                <span className="font-bold text-sm block">2 — Nahi, abhi nahi</span>
                <span className="text-[10px] text-rose-100">Refusal / Escalate outreach</span>
              </div>
              <span className="text-lg">✕</span>
            </button>
          </div>
        </div>
      )}

      {/* Decision & Audit Log Feedback Banner */}
      {result && (
        <div className="p-3.5 bg-emerald-50 border border-emerald-200 rounded-lg text-xs text-emerald-900 space-y-1">
          <p className="font-bold flex items-center gap-1.5 text-emerald-800">
            <span>✓</span> {result.decision}
          </p>
          <p className="text-[11px] text-emerald-700">
            Action: <code className="bg-emerald-100 px-1 py-0.5 rounded font-mono">{result.action_taken}</code> | Logged to Supabase Audit Trail with source <code className="bg-emerald-100 px-1 py-0.5 rounded font-mono">hinglish_voice_simulation</code>.
          </p>
        </div>
      )}
    </div>
  );
}
