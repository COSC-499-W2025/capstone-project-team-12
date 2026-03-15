import React, { useState, useEffect, useRef } from "react";

const fmt = (n: number): string => n.toLocaleString();

function useCountUp(target: number, duration: number = 1200, start: boolean = false): number {
  const [value, setValue] = useState<number>(0);
  useEffect(() => {
    if (!start) return;
    let startTime: number | null = null;
    const step = (ts: number) => {
      if (!startTime) startTime = ts;
      const progress = Math.min((ts - startTime) / duration, 1);
      const ease = 1 - Math.pow(1 - progress, 3);
      setValue(Math.floor(ease * target));
      if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }, [target, duration, start]);
  return value;
}

const Counter: React.FC<{ value: number; label: string; prefix?: string; forceStart?: boolean }> = ({
  value, label, prefix = "", forceStart = false
}) => {
  const ref = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);
  const shouldStart = visible || forceStart;
  const count = useCountUp(value, 1100, shouldStart);

  useEffect(() => {
    const obs = new IntersectionObserver(([e]) => {
      if (e.isIntersecting) setVisible(true);
    }, { threshold: 0.1 });
    if (ref.current) obs.observe(ref.current);
    return () => obs.disconnect();
  }, []);

  return (
    <div ref={ref} className="bg-white px-5 py-4 flex flex-col gap-1">
      <span className="text-2xl font-bold text-slate-800 tracking-tight leading-none">{prefix}{fmt(count)}</span>
      <span className="text-xs font-semibold uppercase tracking-widest text-slate-400">{label}</span>
    </div>
  );
};

export default Counter;