import React, { useState, useEffect, useRef } from "react";
import { type Language } from "../types/types";

const LangBar: React.FC<Language & { index: number }> = ({ name, pct, files, index }) => {
  const ref = useRef<HTMLDivElement>(null);
  const [go, setGo] = useState(false);
  const COLORS = [
    "#d0f0ff", 
    "#7fdfff", 
    "#47caff", 
    "#1e90ff", 
    "#0b61d6", 
    "#034ea2",
    "#002f66", 
    "#4dabff", 
    "#3390ff"  
  ];
  const color = COLORS[index % COLORS.length];

  useEffect(() => {
    const obs = new IntersectionObserver(([e]) => { if (e.isIntersecting) setGo(true); }, { threshold: 0.2 });
    if (ref.current) obs.observe(ref.current);
    return () => obs.disconnect();
  }, []);

  return (
    <div ref={ref} className="flex items-center gap-3">
      <span className="text-xs font-semibold text-slate-500 shrink-0" style={{ width: 100 }}>{name}</span>
      <div className="flex-1 rounded-full overflow-hidden bg-slate-100" style={{ height: 6 }}>
        <div style={{
          height: "100%",
          borderRadius: 9999,
          width: go ? `${pct}%` : "0%",
          transition: `width .9s cubic-bezier(.4,0,.2,1) ${index * 60}ms`,
          background: color,
        }} />
      </div>
      <span className="text-xs font-bold text-indigo-600 text-right shrink-0" style={{ width: 48 }}>{pct.toFixed(1)}%</span>
      <span className="text-xs text-slate-400 text-right shrink-0" style={{ width: 44 }}>{files} files</span>
    </div>
  );
};

export default LangBar;