import React, { useState, useEffect, useRef } from "react";
import { type Language } from "../types";

const LangBar: React.FC<Language & { index: number }> = ({ name, pct, files, index }) => {
  const ref = useRef<HTMLDivElement>(null);
  const [go, setGo] = useState(false);
  const COLORS = ["#e8ff47","#47d9ff","#ff6b6b","#a78bfa","#34d399","#f97316","#f472b6","#60a5fa","#fbbf24"];
  const color = COLORS[index % COLORS.length];

  useEffect(() => {
    const obs = new IntersectionObserver(([e]) => { if (e.isIntersecting) setGo(true); }, { threshold: 0.2 });
    if (ref.current) obs.observe(ref.current);
    return () => obs.disconnect();
  }, []);

  return (
    <div ref={ref} className="flex items-center gap-3">
      <span className="text-[0.72rem] text-[#8899bb] shrink-0 tracking-wide" style={{ width: 100 }}>{name}</span>
      <div className="flex-1 rounded overflow-hidden bg-[#1a1d26]" style={{ height: 6 }}>
        <div style={{
          height: "100%", borderRadius: 3,
          width: go ? `${pct}%` : "0%",
          background: color,
          transition: `width .9s cubic-bezier(.4,0,.2,1) ${index * 60}ms`,
        }} />
      </div>
      <span style={{ width: 48, fontSize: "0.72rem", fontWeight: 700, textAlign: "right", flexShrink: 0, color }}>{pct.toFixed(1)}%</span>
      <span className="text-[0.62rem] text-[#445060] text-right shrink-0" style={{ width: 32 }}>{files}f</span>
    </div>
  );
};

export default LangBar;