import React from "react";

const rankStyles: Record<number, string> = {
  1: "border-amber-300 text-amber-400 bg-amber-50",
  2: "border-slate-300 text-slate-500 bg-slate-50",
  3: "border-orange-300 text-orange-500 bg-orange-50",
};

const RankBadge: React.FC<{ rank: number; total: number }> = ({ rank, total }) => {
  const cls = rankStyles[rank] ?? "border-slate-200 text-slate-400 bg-slate-50";
  return (
    <div className={`text-sm font-bold px-2.5 py-1 rounded-lg border-2 shrink-0 tracking-tight ${cls}`}>
      #{rank}<span className="opacity-50 text-xs">/{total}</span>
    </div>
  );
};

export default RankBadge;