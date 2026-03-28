import React, { useState } from "react";
import Counter from "./counter";
import RankBadge from "./rankbadge";
import ContributionHero from "./contributionhero";
import { type Project } from "../types/types";

const levelColors: Record<string, string> = {
  "Sole Contributor":        "bg-indigo-100 text-indigo-700 border-indigo-200",
  "Top Contributor":         "bg-amber-100 text-amber-700 border-amber-200",
  "Major Contributor":       "bg-violet-100 text-violet-700 border-violet-200",
  "Significant Contributor": "bg-sky-100 text-sky-700 border-sky-200",
  "Contributor":             "bg-slate-100 text-slate-600 border-slate-200",
};

function Highlight({ text, query }: { text: string; query?: string }) {
  if (!query?.trim()) return <>{text}</>;
  const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, "gi");
  const parts = text.split(regex);
  return (
    <>
      {parts.map((part, i) =>
        regex.test(part) ? (
          <mark key={i} className="bg-amber-200 text-amber-900 rounded px-0.5 font-semibold">{part}</mark>
        ) : (
          <span key={i}>{part}</span>
        )
      )}
    </>
  );
}

const ProjectCard: React.FC<{
  project: Project;
  index: number;
  onEdit?: () => void;
  searchQuery?: string;
}> = ({ project, index, onEdit, searchQuery }) => {
  const [open, setOpen] = useState(false);

  const levelCls = levelColors[project.contribution.level] ?? "bg-slate-100 text-slate-600 border-slate-200";

  return (
    <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden hover:border-indigo-200 hover:shadow-sm transition-all">

      {/* Card header */}
      <div
        className="flex items-center justify-between px-5 pt-5 pb-3 cursor-pointer gap-4 flex-wrap"
        onClick={() => setOpen(!open)}
      >
        <div className="flex items-center gap-4">
          <RankBadge rank={project.contribution.rank} total={project.contribution.teamSize} />
          <div>
            <p className="text-sm font-semibold text-slate-800 tracking-tight">
              <Highlight text={project.name} query={searchQuery} />
            </p>
            <p className="text-xs text-slate-400 mt-0.5">
              <Highlight text={project.timeline} query={searchQuery} />
              {" · "}
              <Highlight text={project.duration} query={searchQuery} />
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className={`text-xs font-semibold px-2.5 py-0.5 rounded-full border ${levelCls}`}>
            <Highlight text={project.contribution.level} query={searchQuery} />
          </span>
          {onEdit && (
            <button
              onClick={e => { e.stopPropagation(); onEdit(); }}
              aria-label={`Edit project ${index}`}
              className="text-[11px] font-bold tracking-[0.08em] uppercase text-[#6378ff] border border-[#6378ff]/25 rounded-lg px-3 py-1 hover:bg-[#6378ff]/5 transition-all"
            >
              Edit
            </button>
          )}
          <svg
            className={`w-4 h-4 text-slate-400 transition-transform duration-200 ${open ? "rotate-180" : ""}`}
            fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"
          >
            <path d="M6 9l6 6 6-6" />
          </svg>
        </div>
      </div>

      {/* Role + insight */}
      <div className="px-5 pb-4 flex items-start gap-3 flex-wrap">
        <span className="text-xs font-semibold px-2.5 py-0.5 bg-slate-100 text-slate-500 rounded-full shrink-0 mt-0.5">
          <Highlight text={project.role} query={searchQuery} />
        </span>
        <span className="text-xs text-slate-500 leading-relaxed flex-1">
          <Highlight text={project.insight} query={searchQuery} />
        </span>
      </div>

      <ContributionHero contribution={project.contribution} />

      {/* My stats grid */}
      <div className="grid gap-px bg-slate-100 border-t border-slate-100" style={{ gridTemplateColumns: "repeat(auto-fit,minmax(110px,1fr))" }}>
        <Counter value={project.mine.commits} label="my commits" />
        <Counter value={project.mine.added}   label="lines added" prefix="+" />
        <Counter value={project.mine.net}     label="net lines" />
        <Counter value={project.mine.files}   label="files touched" />
      </div>

      {/* Expandable section */}
      <div
        className="overflow-hidden transition-[max-height] duration-[450ms] ease-in-out"
        style={{ maxHeight: open ? "800px" : "0" }}
      >
        <div className="px-5 pt-5 pb-3 border-t border-slate-100 space-y-4">

          {/* Project totals */}
          <div>
            <p className="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-3">Project Totals</p>
            <div className="grid gap-px bg-slate-100 rounded-xl overflow-hidden" style={{ gridTemplateColumns: "repeat(auto-fit,minmax(110px,1fr))" }}>
              <Counter value={project.totals.commits} label="total commits" forceStart={open} />
              <Counter value={project.totals.files}   label="total files"   forceStart={open} />
              <Counter value={project.totals.added}   label="lines added"   prefix="+" forceStart={open} />
              <Counter value={project.totals.net}     label="net lines"     forceStart={open} />
            </div>
          </div>

          {/* Contribution share */}
          <div>
            <p className="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-3">Contribution Share</p>
            <div className="relative h-6 bg-slate-100 rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-[width] duration-1000 ease-out"
                style={{
                  width: open ? `${project.contribution.share}%` : "0%",
                  background: "linear-gradient(90deg, #6366f1, #818cf8)",
                }}
              />
              <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs font-bold text-slate-700 pointer-events-none">
                {project.contribution.share}% of total commits
              </span>
            </div>
          </div>

          {/* Technologies */}
          {project.technologies.length > 0 && (
            <div>
              <p className="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-3">Technologies</p>
              <div className="flex flex-wrap gap-1.5 pb-2">
                {project.technologies.map(t => (
                  <span key={t} className="text-xs font-medium px-2.5 py-0.5 bg-indigo-50 border border-indigo-100 rounded-full text-indigo-600">
                    <Highlight text={t} query={searchQuery} />
                  </span>
                ))}
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
};

export default ProjectCard;