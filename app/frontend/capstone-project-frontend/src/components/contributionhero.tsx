import React from "react";
import { type Contribution } from "../types/types";

const levelColors: Record<string, string> = {
  "Sole Contributor":        "text-indigo-700",
  "Top Contributor":         "text-amber-600",
  "Major Contributor":       "text-violet-600",
  "Significant Contributor": "text-sky-600",
  "Contributor":             "text-slate-500",
};

const rankColors: string[] = [
  "text-amber-500",   // 1st — gold
  "text-slate-400",   // 2nd — silver
  "text-orange-400",  // 3rd — bronze
];

const ContributionHero: React.FC<{ contribution: Contribution }> = ({ contribution }) => {
  const { rank, teamSize, share, level } = contribution;
  const rankCls  = rankColors[rank - 1] ?? "text-slate-500";
  const levelCls = levelColors[level] ?? "text-slate-500";

  return (
    <div className="grid grid-cols-3 border-t border-slate-100">

      {/* Team Rank */}
      <div className="bg-slate-50 flex flex-col items-center justify-center py-5 gap-1">
        <div className="flex items-baseline gap-0.5">
          <span className={`text-4xl font-bold leading-none tracking-tight ${rankCls}`}>#{rank}</span>
          <span className="text-xl font-semibold text-slate-300 leading-none">/{teamSize}</span>
        </div>
        <span className="text-xs font-semibold uppercase tracking-widest text-slate-400">Team Rank</span>
      </div>

      {/* Commit Share */}
      <div className="bg-slate-50 flex flex-col items-center justify-center py-5 gap-1 border-x border-slate-100">
        <span className="text-4xl font-bold leading-none tracking-tight text-slate-800">{share}%</span>
        <span className="text-xs font-semibold uppercase tracking-widest text-slate-400">of Commits</span>
      </div>

      {/* Contribution Level */}
      <div className="bg-slate-50 flex flex-col items-center justify-center py-5 gap-1">
        <span className={`text-sm font-bold uppercase tracking-wide text-center leading-snug ${levelCls}`}>{level}</span>
        <span className="text-xs font-semibold uppercase tracking-widest text-slate-400">Level</span>
      </div>

    </div>
  );
};

export default ContributionHero;