import React, { useState, useEffect } from "react";

interface ProgressPageProps {
  onComplete: () => void;
}

const ProgressPage: React.FC<ProgressPageProps> = ({ onComplete }) => {
  const [progress, setProgress] = useState<number>(0);
  const [statusText, setStatusText] = useState<string>("Initializing pipeline...");

  //Effect 1: just handle the counting
  useEffect(() => {
    const interval = setInterval(() => {
      setProgress((prev) => {
        //if we are at or above 100, stop increasing
        if (prev >= 100) return 100;
        
        const next = prev + Math.floor(Math.random() * 10) + 5;
        return next > 100 ? 100 : next;
      });
    }, 800);

    return () => clearInterval(interval);
  }, []);

  //effect 2: watch the progress number and update text/trigger redirect
  useEffect(() => {
    if (progress >= 100) {
      setStatusText("Analysis complete! Redirecting...");
      
      //trigger the redirect safely outside the state updater
      const timer = setTimeout(() => {
        onComplete();
      }, 1000);
      
      return () => clearTimeout(timer);
    } 
    
    //update text based on the current progress
    if (progress > 20 && progress < 50) {
      setStatusText("Extracting metadata & code...");
    } else if (progress >= 50 && progress < 80) {
      setStatusText("Running topic analysis...");
    } else if (progress >= 80 && progress < 100) {
      setStatusText("Generating LLM insights...");
    }
  }, [progress, onComplete]);

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-8 bg-black">
      <div className="max-w-lg w-full flex flex-col items-center gap-8 bg-[#111318] p-10 rounded-xl border border-gray-800 shadow-2xl">
        
        <div className="text-center flex flex-col gap-2">
          <h1 className="text-3xl font-bold tracking-tight text-white">
            Processing Project
          </h1>
          <p className="text-[0.7rem] text-[#556070] tracking-widest uppercase">
            Please do not close this tab
          </p>
        </div>

        <div className="relative flex items-center justify-center w-24 h-24">
          <div className="absolute inset-0 border-4 border-[#556070] border-t-blue-500 rounded-full animate-spin"></div>
          <span className="text-lg font-bold text-white">{progress}%</span>
        </div>

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
    </div>
  );
};

export default ProgressPage;