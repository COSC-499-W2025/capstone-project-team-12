import StatCard from "./StatCard";
import SectionCard from "./SectionCard";
import type { Project } from "../insightTypes";

interface DeploymentTabProps {
  p: Project;
}

export default function DeploymentTab({ p }: DeploymentTabProps) {
  return (
    <div className="space-y-5">
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <StatCard label="CI/CD Files"  value={p.deployment.ciFiles}     sub={p.deployment.hasCI ? "CI detected" : "No CI detected"}         accent={p.deployment.hasCI} />
        <StatCard label="Docker Files" value={p.deployment.dockerFiles} sub={p.deployment.hasDocker ? "Containerized" : "No Docker config"} accent={p.deployment.hasDocker} />
        <StatCard label="Infra Files"  value={p.deployment.infraFiles}  sub="infrastructure configs" />
      </div>

      <SectionCard title="CI/CD Status" icon="🚀">
        <div className="space-y-3">
          {[
            { label: "Continuous Integration",    active: p.deployment.hasCI },
            { label: "Docker / Containerization", active: p.deployment.hasDocker },
          ].map(({ label, active }) => (
            <div key={label} className="flex items-center gap-3">
              <span className={`w-2.5 h-2.5 rounded-full shrink-0 ${active ? "bg-green-500" : "bg-slate-300"}`} />
              <span className={`text-sm font-medium ${active ? "text-slate-700" : "text-slate-400"}`}>{label}</span>
              <span className={`ml-auto text-xs px-2 py-0.5 rounded-full font-semibold ${active ? "bg-green-100 text-green-700" : "bg-slate-100 text-slate-400"}`}>
                {active ? "Detected" : "Not found"}
              </span>
            </div>
          ))}
        </div>
      </SectionCard>

      <SectionCard title="Version Control" icon="🔀">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: "Total Commits",  value: p.versionControl.totalCommits },
            { label: "Branches",       value: p.versionControl.branches },
            { label: "Merge Commits",  value: p.versionControl.mergeCommits },
            { label: "Avg Msg Length", value: `${p.versionControl.avgCommitMessageLength}c` },
          ].map(({ label, value }) => (
            <div key={label} className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-center">
              <p className="text-2xl font-bold text-slate-800">{value}</p>
              <p className="text-xs text-slate-400 uppercase tracking-wide mt-1">{label}</p>
            </div>
          ))}
        </div>
      </SectionCard>
    </div>
  );
}
