import StatCard from "./StatCard";
import SectionCard from "./SectionCard";
import TechBadge from "./TechBadge";
import FileExtensionSection from "./FileExtensionSection";
import type { Project } from "../types/insightTypes";

interface OverviewTabProps {
  p: Project;
}

export default function OverviewTab({ p }: OverviewTabProps) {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Rank by Commits" value={`#${p.contribution.rank}`} sub={`out of ${p.collaboration.teamSize}`} accent />
        <StatCard label="Your Share" value={`${p.collaboration.contributionShare}%`} sub="of total contributions" accent />
        <StatCard label="Percentile" value={`${p.contribution.percentile}%`} />
        <StatCard label="Team Size" value={p.collaboration.teamSize} sub={p.collaboration.isCollaborative ? "collaborative" : "solo project"} />
      </div>

      <div className="grid md:grid-cols-2 gap-5">
        <SectionCard title="Your Role" icon="🧑‍💻">
          <div className="flex items-start gap-3">
            <span className="px-3 py-1.5 rounded-full bg-indigo-600 text-white text-xs font-bold whitespace-nowrap shrink-0">
              {p.userRole.title}
            </span>
            <p className="text-sm text-slate-600 leading-relaxed">{p.userRole.description}</p>
          </div>
        </SectionCard>

        <SectionCard title="Key Technologies" icon="⚙️">
          <div className="flex flex-wrap gap-2">
            {p.technologies.map((t) => <TechBadge key={t.name} name={t.name} uses={t.uses} />)}
          </div>
          <p className="text-xs text-slate-400 mt-3">Badge darkness = frequency of use</p>
        </SectionCard>
      </div>

      <FileExtensionSection fileExtensions={p.fileExtensions} />

      <SectionCard title="Project Timeline" icon="📅">
        <div className="flex items-center gap-4">
          <div className="text-center">
            <p className="text-xs text-slate-400 uppercase tracking-wide mb-1">Start</p>
            <span className="px-4 py-2 rounded-xl bg-indigo-50 text-indigo-700 font-semibold text-sm">{p.timeline.start}</span>
          </div>
          <div className="flex-1 h-0.5 bg-gradient-to-r from-indigo-300 to-indigo-500 rounded-full" />
          <div className="text-center">
            <p className="text-xs text-slate-400 uppercase tracking-wide mb-1">End</p>
            <span className="px-4 py-2 rounded-xl bg-indigo-600 text-white font-semibold text-sm">{p.timeline.end}</span>
          </div>
        </div>
      </SectionCard>
    </div>
  );
}
