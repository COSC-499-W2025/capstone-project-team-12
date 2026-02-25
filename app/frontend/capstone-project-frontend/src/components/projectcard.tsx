import React, { useState } from "react";
import Counter from "./counter";
import RankBadge from "./rankbadge";
import ContributionHero from "./contributionhero";
import { type Project } from "../types";

const ProjectCard: React.FC<{ project: Project; index: number }> = ({ project, index }) => {
  const [open, setOpen] = useState(false);
  const levelColor = project.contribution.level === "Top Contributor" ? "#e8ff47" : "#47d9ff";

  return (
    <div className="bg-[#111318] border border-[#1e2330] rounded-md mb-4 overflow-hidden fade-in-card" style={{ animationDelay: `${index * 150}ms` }}>
      <div className="flex items-center justify-between px-6 pt-5 pb-3 cursor-pointer gap-4 flex-wrap" onClick={() => setOpen(!open)}>
        <div className="flex items-center gap-4">
          <RankBadge rank={project.contribution.rank} total={project.contribution.teamSize} />
          <div>
            <div className="text-[1.05rem] font-semibold text-[#eef1f8] tracking-tight">{project.name}</div>
            <div className="text-[0.68rem] text-[#556070] mt-0.5 tracking-wide">{project.timeline} · {project.duration}</div>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <span style={{ fontSize: "0.6rem", padding: "3px 10px", border: "1px solid", borderRadius: 20, letterSpacing: "0.1em", textTransform: "uppercase", borderColor: levelColor, color: levelColor }}>
            {project.contribution.level}
          </span>
          <span className="text-[0.7rem] text-[#556070] select-none">{open ? "▲" : "▼"}</span>
        </div>
      </div>

      <div className="px-6 pb-4 flex items-start gap-3 flex-wrap">
        <span className="text-[0.62rem] px-2 py-0.5 bg-[#1a1d26] border border-[#2a3040] rounded text-[#8899bb] tracking-wide shrink-0 mt-0.5">{project.role}</span>
        <span className="text-[0.78rem] text-[#667080] leading-relaxed flex-1">{project.insight}</span>
      </div>

      <ContributionHero contribution={project.contribution} />

      <div className="grid gap-px bg-[#1e2330] border-t border-[#1e2330]" style={{ gridTemplateColumns: "repeat(auto-fit,minmax(110px,1fr))" }}>
        <Counter value={project.mine.commits} label="my commits" />
        <Counter value={project.mine.added}   label="lines added" prefix="+" />
        <Counter value={project.mine.net}     label="net lines" />
        <Counter value={project.mine.files}   label="files touched" />
      </div>

      <div className="overflow-hidden transition-[max-height] duration-[450ms] ease-in-out" style={{ maxHeight: open ? "800px" : "0" }}>
        <div className="px-6 pt-5 pb-2 border-t border-[#1e2330]">
          <div className="text-[0.6rem] tracking-[0.18em] text-[#556070] mb-3 mt-5 uppercase">PROJECT TOTALS</div>
          <div className="grid gap-px bg-[#1e2330] rounded overflow-hidden" style={{ gridTemplateColumns: "repeat(auto-fit,minmax(110px,1fr))" }}>
            <Counter value={project.totals.commits} label="total commits" forceStart={open} />
            <Counter value={project.totals.files}   label="total files" forceStart={open} />
            <Counter value={project.totals.added}   label="lines added" prefix="+" forceStart={open} />
            <Counter value={project.totals.net}     label="net lines" forceStart={open} />
          </div>

          <div className="text-[0.6rem] tracking-[0.18em] text-[#556070] mb-3 mt-5 uppercase">CONTRIBUTION SHARE</div>
          <div className="h-6 bg-[#1a1d26] rounded overflow-hidden relative">
            <div className="h-full rounded transition-[width] duration-1000 ease-out" style={{ width: open ? `${project.contribution.share}%` : "0%", background: "linear-gradient(90deg,#e8ff47,#a8e030)" }} />
            <span className="absolute right-3 top-1/2 -translate-y-1/2 text-[0.65rem] font-bold text-[#111318] pointer-events-none mix-blend-multiply">
              {project.contribution.share}% of total commits
            </span>
          </div>

          {project.technologies.length > 0 && (
            <>
              <div className="text-[0.6rem] tracking-[0.18em] text-[#556070] mb-3 mt-5 uppercase">TECHNOLOGIES</div>
              <div className="flex flex-wrap gap-1.5 pb-3">
                {project.technologies.map(t => (
                  <span key={t} className="text-[0.62rem] px-2.5 py-0.5 bg-[#1a1d26] border border-[#2a3040] rounded text-[#667080]">{t}</span>
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProjectCard;