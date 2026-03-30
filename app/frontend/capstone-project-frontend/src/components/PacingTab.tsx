import StatCard from "./StatCard";
import SectionCard from "./SectionCard";
import PacingBar from "./PacingBar";
import CommitHeatmap from "./CommitHeatmap";
import type { Project } from "../types/insightTypes";

interface PacingTabProps {
  p: Project;
}

export default function PacingTab({ p }: PacingTabProps) {
  return (
    <div className="space-y-5">
      <CommitHeatmap commits={p.rawCommits ?? []} />
      <div className="grid md:grid-cols-2 gap-4">
        <StatCard label="Avg Lines per Commit" value={p.pacing.avgLinesPerCommit} accent />
        <StatCard label="Commits Made in the Last 1/4 of Project" value={`${p.pacing.endHeavyPercent}%`} accent />
      </div>
      <SectionCard title="Commit Distribution" icon="📊">
        <PacingBar percent={p.pacing.endHeavyPercent} message={p.pacing.commitConsistency} />
      </SectionCard>
      <SectionCard title="Contribution Level" icon="🏅">
        <div className="flex items-center gap-3">
          <span className="px-3 py-1.5 rounded-full bg-amber-100 text-amber-700 text-xs font-bold shrink-0">
            {p.contribution.level}
          </span>
          <p className="text-sm text-slate-600">
            Ranked <strong>#{p.contribution.rank}</strong> out of {p.collaboration.teamSize} contributor{p.collaboration.teamSize !== 1 ? "s" : ""} with a{" "}
            <strong>{p.collaboration.contributionShare}%</strong> share of all commits.
          </p>
        </div>
      </SectionCard>
    </div>
  );
}