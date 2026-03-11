import React from "react";
import { type Contribution } from "../types/types";

const ContributionHero: React.FC<{ contribution: Contribution }> = ({ contribution }) => {
  const { rank, teamSize, share, level } = contribution;
  const medalColors = ["#FFD700", "#C0C0C0", "#CD7F32"];
  const rankColor = medalColors[rank - 1] || "#8899aa";
  const levelColors: Record<string, string> = {
    "Sole Contributor":        "#e8ff47",
    "Top Contributor":         "#FFD700",
    "Major Contributor":       "#a78bfa",
    "Significant Contributor": "#47d9ff",
    "Contributor":             "#8899bb",
  };
  const levelColor = levelColors[level] ?? "#8899bb";

  return (
    <div className="grid grid-cols-3 border-t border-[#1e2330]">
      <div className="bg-[#111318] flex flex-col items-center justify-center py-5 gap-1.5">
        <div className="flex items-baseline gap-0.5">
          <span style={{ fontSize: "2.8rem", fontWeight: 700, lineHeight: 1, letterSpacing: "-0.04em", fontFamily: "'Syne',monospace", color: rankColor }}>#{rank}</span>
          <span style={{ fontSize: "1.4rem", fontWeight: 600, lineHeight: 1, color: rankColor, opacity: 0.45 }}>/{teamSize}</span>
        </div>
        <span className="text-[0.58rem] text-[#556070] tracking-[0.16em] uppercase">Team Rank</span>
      </div>
      <div className="bg-[#111318] flex flex-col items-center justify-center py-5 gap-1.5 border-x border-[#1e2330]">
        <span className="text-[2.8rem] font-bold leading-none tracking-tight text-white" style={{ fontFamily: "'Syne',monospace" }}>{share}%</span>
        <span className="text-[0.58rem] text-[#556070] tracking-[0.16em] uppercase">of Commits</span>
      </div>
      <div className="bg-[#111318] flex flex-col items-center justify-center py-5 gap-1.5">
        <span style={{ fontSize: "0.75rem", fontWeight: 700, letterSpacing: "0.08em", textTransform: "uppercase", textAlign: "center", lineHeight: 1.3, color: levelColor }}>{level}</span>
        <span className="text-[0.58rem] text-[#556070] tracking-[0.16em] uppercase">Level</span>
      </div>
    </div>
  );
};

export default ContributionHero;