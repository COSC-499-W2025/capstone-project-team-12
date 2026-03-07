import React, { useState, useEffect } from "react";

interface ProgressPageProps {
  onComplete: () => void;
}

const ProgressPage: React.FC<ProgressPageProps> = ({ onComplete }) => {
  const [progress, setProgress] = useState<number>(0);
  const [statusText, setStatusText] = useState<string>("Initializing pipeline...");

  //effect 1: just handle the counting
  useEffect(() => {
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) return 100;
        
        const next = prev + Math.floor(Math.random() * 10) + 5;
        return next > 100 ? 100 : next;
      });
    }, 800);

    return () => clearInterval(interval);
  }, []);

  // effect 2: watch the progress number and update text
  useEffect(() => {
    if (progress >= 100) {
      setStatusText("Analysis complete!");
      return; 
    } 
    
    if (progress > 20 && progress < 50) {
      setStatusText("Extracting metadata & code...");
    } else if (progress >= 50 && progress < 80) {
      setStatusText("Running topic analysis...");
    } else if (progress >= 80 && progress < 100) {
      setStatusText("Generating LLM insights...");
    }
  }, [progress]);

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-8 bg-black">
      <div className="max-w-lg w-full flex flex-col items-center gap-8 bg-[#111318] p-10 rounded-xl border border-gray-800 shadow-2xl">
        
        <div className="text-center flex flex-col gap-2">
          <h1 className="text-3xl font-bold tracking-tight text-white">
            Processing Project
          </h1>
          <p className="text-[0.7rem] text-[#556070] tracking-widest uppercase">
            {progress >= 100 ? "Ready to view results" : "Please do not close this tab"}
          </p>
        </div>

        <div className="relative flex items-center justify-center w-24 h-24">
          {/*change to a solid border when done, spin while loading */}
          {progress >= 100 ? (
            <div className="absolute inset-0 border-4 border-green-500 rounded-full"></div>
          ) : (
            <div className="absolute inset-0 border-4 border-[#556070] border-t-blue-500 rounded-full animate-spin"></div>
          )}
          <span className="text-lg font-bold text-white">{progress}%</span>
        </div>

        <div className="w-full flex flex-col gap-3">
          <div className="w-full bg-black rounded-full h-3 overflow-hidden border border-gray-800">
            <div
              className={`h-full rounded-full transition-all duration-500 ease-out ${
                progress >= 100 ? "bg-green-500" : "bg-blue-600"
              }`}
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <div className="flex justify-between items-center text-xs font-medium text-gray-400">
            <span>{statusText}</span>
            <span>{progress}/100</span>
          </div>
        </div>

        {/* the next Button only renders when progress is 100 */}
        {progress >= 100 && (
          <button
            onClick={onComplete}
            className="w-full bg-blue-600 hover:bg-blue-500 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200 mt-2"
          >
            View Results
          </button>
        )}

      </div>
    </div>
  );
};

export default ProgressPage;