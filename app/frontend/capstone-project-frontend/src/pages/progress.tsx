import React, { useState, useEffect } from "react";

interface ProgressPageProps {
  onComplete: () => void;
}

const ProgressPage: React.FC<ProgressPageProps> = ({ onComplete }) => {  //state to simulate pipeline progress
  const [progress, setProgress] = useState<number>(0);
  const [statusText, setStatusText] = useState<string>("Initializing pipeline...");

  // Simulated progress effect 
  useEffect(() => {
    const interval = setInterval(() => {
      setProgress((prev) => {
        const next = prev + Math.floor(Math.random() * 10) + 5;
        if (next >= 100) {
          clearInterval(interval);
          setStatusText("Analysis complete! Redirecting...");
          return 100;
        }
        
        // Update status text based on progress
        if (next > 20 && next < 50) setStatusText("Extracting metadata & code...");
        else if (next >= 50 && next < 80) setStatusText("Running topic analysis...");
        else if (next >= 80 && next < 100) setStatusText("Generating LLM insights...");

        return next;
      });
    }, 800);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex min-h-screen bg-black text-white">
      {/* sidebar to be added when Devin's code is approved */}

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col items-center justify-center p-8">
        <div className="max-w-lg w-full flex flex-col items-center gap-8 bg-[#111318] p-10 rounded-xl border border-gray-800 shadow-2xl">
          
          {/* Header */}
          <div className="text-center flex flex-col gap-2">
            <h1 className="text-3xl font-bold tracking-tight text-white">
              Processing Project
            </h1>
            <p className="text-[0.7rem] text-[#556070] tracking-widest uppercase">
              Please do not close this tab
            </p>
          </div>

          {/* Animated Spinner */}
          <div className="relative flex items-center justify-center w-24 h-24">
            <div className="absolute inset-0 border-4 border-[#556070] border-t-blue-500 rounded-full animate-spin"></div>
            <span className="text-lg font-bold text-white">{progress}%</span>
          </div>

          {/* Progress Bar & Status Text */}
          <div className="w-full flex flex-col gap-3">
            <div className="w-full bg-black rounded-full h-3 overflow-hidden border border-gray-800">
              <div
                className="bg-blue-600 h-full rounded-full transition-all duration-500 ease-out"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            <div className="flex justify-between items-center text-xs font-medium text-gray-400">
              <span>{statusText}</span>
              <span>{progress}/100</span>
            </div>
          </div>

        </div>
      </main>
    </div>
  );
};

export default ProgressPage;