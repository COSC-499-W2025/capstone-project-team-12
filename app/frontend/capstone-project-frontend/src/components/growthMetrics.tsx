import type { PortfolioData } from "../types/types";

interface GrowthMetricsProps {
  g: NonNullable<PortfolioData['growthMetrics']>;
  earliestProject: string;
  latestProject: string;
}

function GrowthBadge({ value, label, sub }: { value: number; label: string; sub?: string }) {
  const positive = value >= 0;
  const direction = positive ? 'went up' : 'went down';
  const generatedSub = `${sub} ${direction} over time`;

  return (
    <div className="bg-white rounded-2xl border border-slate-100 p-4 flex flex-col gap-1">
      <span className="text-xs font-semibold uppercase tracking-widest text-slate-400">{label}</span>
      <span className={`text-2xl font-bold ${positive ? 'text-blue-600' : 'text-gray-600'}`}>
        {positive ? '+' : ''}{value.toFixed(1)}%
      </span>
      {sub && <span className="text-xs text-slate-400">{generatedSub}</span>}
    </div>
  );
}

export default function GrowthMetrics({ g }: GrowthMetricsProps) {
  if (!g.has_comparison) return null;

  return (
    <div className="mt-10 space-y-6">
      <div>
        <p className="text-xs font-semibold uppercase tracking-widest text-indigo-500 mb-1">Growth & Evolution</p>
        <h2 className="text-2xl font-bold text-slate-800">Progress over time</h2>
        <p className="text-sm text-slate-500 mt-1">
          Comparing <span className="font-semibold text-slate-700">{g.earliest_project}</span>
          {" → "}
          <span className="font-semibold text-slate-700">{g.latest_project}</span>
        </p>
      </div>

      {/* Code Metrics */}
      <div>
        <h3 className="text-sm font-semibold text-slate-600 mb-3">Project Scale</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <GrowthBadge
            value={g.code_metrics.commit_growth}
            label="Project Commits"
            sub="Total number of commits across all users"
          />
          <GrowthBadge
            value={g.code_metrics.file_growth}
            label="Files Touched"
            sub="Total number of files touched by all users"
          />
          <GrowthBadge
            value={g.code_metrics.lines_growth}
            label="Project Size"
            sub="Project size"
          />
          <GrowthBadge
            value={g.code_metrics.user_lines_growth}
            label="Your Net Lines"
            sub="Your personal output"
          />
        </div>
      </div>

      {/* Technology Timeline */}
      <div className="bg-white rounded-2xl border border-slate-100 p-5">
        <h3 className="text-sm font-semibold text-slate-600 mb-4">Technology Progression</h3>
        <div className="space-y-4">
          {(g.framework_timeline_list ?? []).map((proj) => (
            <div key={proj.project_name} className="flex items-start gap-3">
              <div className="text-xs text-slate-400 w-32 shrink-0 pt-1">{proj.date_range}</div>
              <div className="flex-1">
                <p className="text-sm font-medium text-slate-700 mb-1.5">{proj.project_name}</p>
                <div className="flex flex-wrap gap-1">
                  {proj.frameworks.length > 0
                    ? proj.frameworks.map((f: string) => (
                        <span key={f} className="text-xs px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-600 font-medium">
                          {f}
                        </span>
                      ))
                    : <span className="text-xs text-slate-400 italic">No frameworks detected</span>
                  }
                  {proj.total_frameworks > proj.frameworks.length && (
                    <span className="text-xs px-2 py-0.5 rounded-full bg-slate-100 text-slate-400">
                      +{proj.total_frameworks - proj.frameworks.length} more
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Collaboration */}
      <div className="bg-white rounded-2xl border border-slate-100 p-5">
        <h3 className="text-sm font-semibold text-slate-600 mb-2">Collaboration</h3>
        {/* {g.collaboration_evolution.collaboration_summary && (
          <p className="text-sm text-slate-500 mb-3">{g.collaboration_evolution.collaboration_summary}</p>
        )} */}
        <div className="flex gap-6">
          <div>
            <p className="text-xs text-slate-400">First project</p>
            <p className="text-sm font-semibold text-slate-700">{g.collaboration_evolution.earliest_level}</p>
            <p className="text-xs text-slate-400">{g.collaboration_evolution.earliest_team_size} contributors</p>
          </div>
          <div className="flex items-center text-slate-300 text-xl">→</div>
          <div>
            <p className="text-xs text-slate-400">Latest project</p>
            <p className="text-sm font-semibold text-indigo-600">{g.collaboration_evolution.latest_level}</p>
            <p className="text-xs text-slate-400">{g.collaboration_evolution.latest_team_size} contributors</p>
          </div>
        </div>
      </div>

      {/* Testing */}
      <div className="bg-white rounded-2xl border border-slate-100 p-5">
        <h3 className="text-sm font-semibold text-slate-600 mb-2">Testing Evolution</h3>
        {g.testing_evolution.testing_status
          ? <p className="text-sm text-slate-700">{g.testing_evolution.testing_status}</p>
          : (
            <p className="text-sm text-slate-500">
              {g.testing_evolution.earliest_has_tests ? "Had tests" : "No tests"} in first project
              {" → "}
              {g.testing_evolution.latest_has_tests ? "has tests" : "no tests"} in latest project.
            </p>
          )
        }
        {g.testing_evolution.coverage_improvement > 0 && (
          <p className="text-sm text-emerald-600 font-semibold mt-1">
            +{g.testing_evolution.coverage_improvement}% coverage improvement
          </p>
        )}
      </div>

      {/* Role — only if changed */}
      {g.role_evolution.role_changed && (
        <div className="bg-white rounded-2xl border border-slate-100 p-5">
          <h3 className="text-sm font-semibold text-slate-600 mb-2">Role Evolution</h3>
          <div className="flex gap-4 items-center">
            <span className="text-sm text-slate-500">{g.role_evolution.earliest_role}</span>
            <span className="text-slate-300">→</span>
            <span className="text-sm font-semibold text-indigo-600">{g.role_evolution.latest_role}</span>
          </div>
        </div>
      )}
    </div>
  );
}