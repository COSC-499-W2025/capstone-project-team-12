import StatCard from "./StatCard";
import SectionCard from "./SectionCard";
import type { Project } from "../types/insightTypes";

interface DeploymentTabProps {
  p: Project;
}

export default function DeploymentTab({ p }: DeploymentTabProps) {
  return (
    <div className="space-y-5">
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <StatCard label="CI/CD Files"  value={p.deployment.ciFiles}     sub={p.deployment.hasCI ? "CI detected" : "No CI detected"}         accent={p.deployment.hasCI} />
        <StatCard label="Docker Files" value={p.deployment.dockerFiles} sub={p.deployment.hasDocker ? "Containerized" : "No Docker config"} accent={p.deployment.hasDocker} />
      </div>

      <SectionCard title="Deployment Overview" icon="🚀">
        <div className="space-y-3">
          {[
            { label: "Continuous Integration",    active: p.deployment.hasCI,     tools: p.deployment.cicdTools },
            { label: "Docker / Containerization", active: p.deployment.hasDocker, tools: p.deployment.containerizationTools },
          ].map(({ label, active, tools }) => (
            <div key={label} className="flex items-center gap-3">
              <span className={`w-2.5 h-2.5 rounded-full shrink-0 ${active ? "bg-green-500" : "bg-slate-300"}`} />
              <span className={`text-sm font-medium ${active ? "text-slate-700" : "text-slate-400"}`}>{label}</span>
              {active && tools.length > 0 && (
                <span className="text-xs text-slate-500">({tools.join(", ")})</span>
              )}
              <span className={`ml-auto text-xs px-2 py-0.5 rounded-full font-semibold ${active ? "bg-green-100 text-green-700" : "bg-slate-100 text-slate-400"}`}>
                {active ? "Detected" : "Not found"}
              </span>
            </div>
          ))}

          <div className="flex items-center gap-3">
            <span className={`w-2.5 h-2.5 rounded-full shrink-0 ${p.deployment.hostingPlatforms.length > 0 ? "bg-green-500" : "bg-slate-300"}`} />
            <span className={`text-sm font-medium ${p.deployment.hostingPlatforms.length > 0 ? "text-slate-700" : "text-slate-400"}`}>Hosting Platform</span>
            {p.deployment.hostingPlatforms.length > 0 && (
              <span className="text-xs text-slate-500">({p.deployment.hostingPlatforms.join(", ")})</span>
            )}
            <span className={`ml-auto text-xs px-2 py-0.5 rounded-full font-semibold ${p.deployment.hostingPlatforms.length > 0 ? "bg-green-100 text-green-700" : "bg-slate-100 text-slate-400"}`}>
              {p.deployment.hostingPlatforms.length > 0 ? "Detected" : "Not found"}
            </span>
          </div>
        </div>
      </SectionCard>
    </div>
  );
}
