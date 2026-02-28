import React from "react";

const RankBadge: React.FC<{ rank: number; total: number }> = ({ rank, total }) => {
  const medals = ["#FFD700", "#C0C0C0", "#CD7F32"];
  const color = medals[rank - 1] || "#8899aa";
  return (
    <div 
      style={{ fontSize: "0.9rem", fontWeight: 700, padding: "4px 10px", borderRadius: 4, flexShrink: 0, letterSpacing: "-0.02em", border: `2px solid ${color}`, color }}
    >
      #{rank}<span style={{ opacity: 0.5, fontSize: "0.65em" }}>/{total}</span>
    </div>
  );
};

export default RankBadge;