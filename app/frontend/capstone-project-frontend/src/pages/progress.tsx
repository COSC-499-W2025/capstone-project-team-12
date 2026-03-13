// src/pages/progress.tsx
import React, { useState, useEffect } from "react";

interface ProgressPageProps {
  onComplete: () => void;
  isProcessing: boolean;
}

const ProgressPage: React.FC<ProgressPageProps> = ({ onComplete, isProcessing }) => {
  const [progress, setProgress] = useState<number>(0);
  const [statusText, setStatusText] = useState<string>("Initializing pipeline...");

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) return 100;
        
        const next = prev + Math.floor(Math.random() * 10) + 5;
        // Cap at 95% as long as the API is still thinking
        if (isProcessing) return Math.min(next, 95);
        return next > 100 ? 100 : next;
      });
    }, 800);

    return () => clearInterval(interval);
  }, [isProcessing]);

  // Jump to 100% when the API finishes
  useEffect(() => {
    if (!isProcessing && progress > 0) {
      setProgress(100);
    }
  }, [isProcessing, progress]);

  useEffect(() => {
    if (progress >= 100) {
      setStatusText("Analysis complete!");
    } else if (progress > 20 && progress < 50) {
      setStatusText("Extracting metadata & code...");
    } else if (progress >= 50 && progress < 80) {
      setStatusText("Running topic analysis...");
    } else if (progress >= 80 && progress < 100) {
      setStatusText("Generating LLM insights...");
    }
  }, [progress]);

  // Derive the exact completion state directly from the progress number
  const isDone = progress >= 100;

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-8 bg-[#f8f9fc] relative overflow-hidden font-sans">
      
      <div className="absolute inset-0 pointer-events-none" style={{ backgroundImage: `radial-gradient(ellipse at 70% 0%, rgba(99,120,255,0.07) 0%, transparent 55%), radial-gradient(ellipse at 10% 100%, rgba(167,139,250,0.05) 0%, transparent 50%)` }} />
      
      <div className="max-w-lg w-full flex flex-col items-center gap-8 bg-white p-10 rounded-2xl border border-gray-100 shadow-[0_20px_60px_rgba(0,0,0,0.08)] relative z-10">
        
        <div className="text-center flex flex-col gap-2">
          <p className="text-[11px] font-bold tracking-[0.12em] uppercase text-[#6378ff] m-0">
            {isDone ? "Ready to view results" : "Please do not close this tab"}
          </p>
          <h1 className="text-[26px] font-extrabold tracking-tight text-[#0f1629] m-0 leading-snug">
            Processing Project
          </h1>
        </div>

        <div className="relative flex items-center justify-center w-24 h-24">
          {isDone ? (
            <div className="absolute inset-0 border-4 border-[#10b981] rounded-full"></div>
          ) : (
            <div className="absolute inset-0 border-4 border-[#eef0f6] border-t-[#6378ff] rounded-full animate-spin"></div>
          )}
          <span className="text-lg font-bold text-[#0f1629]">{progress}%</span>
        </div>

        <div className="w-full flex flex-col gap-3">
          <div className="w-full bg-[#eef0f6] rounded-full h-3 overflow-hidden border border-gray-200 shadow-inner">
            <div
              className="h-full rounded-full transition-all duration-300 ease-out"
              style={{ 
                width: `${progress}%`, 
                // Uses the blue gradient until progress hits exactly 100
                background: isDone ? '#10b981' : 'linear-gradient(135deg, #6378ff 0%, #a78bfa 100%)' 
              }}
            ></div>
          </div>
          <div className="flex justify-between items-center text-xs font-semibold text-[#6b7280]">
            <span>{statusText}</span>
            <span>{progress}/100</span>
          </div>
        </div>

        {/* The Next Button is now conditionally rendered ONLY when isDone is true */}
        {isDone && (
          <button
            onClick={onComplete}
            className="w-full py-3.5 px-6 rounded-xl font-bold transition-all duration-300 mt-2 border-none flex items-center justify-center gap-2 bg-gradient-to-r from-[#6378ff] to-[#a78bfa] text-white shadow-[0_4px_20px_rgba(99,120,255,0.3)] hover:shadow-[0_6px_25px_rgba(99,120,255,0.4)] hover:-translate-y-0.5 cursor-pointer"
          >
            View Results
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>
            </svg>
          </button>
        )}

      </div>
    </div>
  );
};

export default ProgressPage;