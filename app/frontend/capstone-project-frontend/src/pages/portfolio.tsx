import { type PortfolioData } from "../types/types";
import { useEffect, useState } from "react";
import ProjectCard from "../components/projectcard";
import LangBar from "../components/langbar";

// SAMPLE DATA
const PORTFOLIO_DATA: PortfolioData = {
  developer: "Your Name",
  coreCompetencies: ["Mobile App Development", "Backend Development", "Web Development"],
  languages: [
    { name: "XML",          pct: 34.7, files: 50 },
    { name: "Java",         pct: 18.8, files: 27 },
    { name: "PHP",          pct: 11.8, files: 17 },
    { name: "CSS",          pct:  9.7, files: 14 },
    { name: "JavaScript",   pct:  9.0, files: 13 },
    { name: "HTML",         pct:  6.9, files: 10 },
    { name: "Kotlin",       pct:  2.1, files:  3 },
    { name: "Transact-SQL", pct:  1.4, files:  2 },
    { name: "Markdown",     pct:  0.7, files:  1 },
  ],
  projects: [
    {
      id: 1,
      name: "example-1",
      timeline: "Jan 2025 – Apr 2025",
      duration: "41 days",
      role: "Full-Stack Developer",
      insight: "Contributed a substantial amount of new code, indicating a strong role in implementing features and expanding the project's functionality.",
      contribution: { level: "Top Contributor", teamSize: 5, rank: 2, percentile: 85, share: 65.0 },
      totals: { commits: 142, files: 362, added: 11560, deleted: 3144, net: 8416 },
      mine:   { commits: 142, added: 6523, deleted: 2096, net: 4427, files: 162 },
      technologies: ["Python", "FastAPI", "PostgreSQL", "Docker", "Flask"],
    },
    {
      id: 2,
      name: "example-2",
      timeline: "Jun 2024 – Jan 2025",
      duration: "3 days",
      role: "UI/UX Developer",
      insight: "Balanced contribution pattern across additions, modifications, and deletions throughout the codebase.",
      contribution: { level: "Solo Developer", teamSize: 1, rank: 1, percentile: 100, share: 100.0 },
      totals: { commits: 87,  files: 326, added: 16669, deleted: 857,  net: 15812 },
      mine:   { commits: 87,  added: 836,  deleted: 16,   net: 820,  files: 26 },
      technologies: ["React", "TypeScript", "Tailwind CSS", "Vite"],
    },
  ],
};


// --------- ENDPOINT ---------------
const API_BASE = "http://localhost:8080";

async function fetchPortfolio(portfolioId: number): Promise<PortfolioData> {
  const res = await fetch(`${API_BASE}/portfolio/${portfolioId}`);
  if (!res.ok) throw new Error(`Failed to fetch portfolio: ${res.status} ${res.statusText}`);
  const data = await res.json();
  const d = data.portfolio_data;

  return {
    developer: d.result_id ?? "Developer",
    coreCompetencies: d.skill_timeline?.high_level_skills ?? [],
    languages: (d.skill_timeline?.language_progression ?? []).map((l: any) => ({
      name: l.name,
      pct: l.percentage,
      files: l.file_count,
    })),
    projects: (d.projects_detail ?? []).map((p: any) => ({
      id: p.name,
      name: p.name,
      timeline: p.date_range,
      duration: `${p.duration_days} days`,
      role: p.user_role?.role ?? "",
      insight: p.user_role?.blurb ?? "",
      contribution: {
        level: p.contribution?.level ?? "",
        teamSize: p.contribution?.team_size ?? 1,
        rank: p.contribution?.rank ?? 1,
        percentile: p.contribution?.percentile ?? 0,
        share: p.contribution?.contribution_share ?? 0,
      },
      totals: {
        commits: p.statistics?.commits ?? 0,
        files: p.statistics?.files ?? 0,
        added: p.statistics?.additions ?? 0,
        deleted: p.statistics?.deletions ?? 0,
        net: p.statistics?.net_lines ?? 0,
      },
      mine: {
        commits: p.statistics?.user_commits ?? 0,
        added: p.statistics?.user_lines_added ?? 0,
        deleted: p.statistics?.user_lines_deleted ?? 0,
        net: p.statistics?.user_net_lines ?? 0,
        files: p.statistics?.user_files_modified ?? 0,
      },
      technologies: p.frameworks_summary?.top_frameworks ?? [],
    })),
  };
}


export default function DevPortfolio({ data: dataProp, onComplete, onPrevious, portfolioId } : {
  data?: PortfolioData;
  onComplete?: () => void;
  onPrevious?: () => void;
  portfolioId?: number | null;
}) {

  const [data, setData] = useState<PortfolioData>(dataProp ?? PORTFOLIO_DATA);
  const [loading, setLoading] = useState(portfolioId != null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (portfolioId == null) return;
    fetchPortfolio(portfolioId)
      .then(d  => { setData(d); setLoading(false); })
      .catch(e => { setError(e.message); setLoading(false); });
  }, [portfolioId]);

  if (loading) return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center">
      <p className="text-sm text-slate-400">Loading portfolio…</p>
    </div>
  );

  return (
    <div className="min-h-screen bg-slate-50 font-sans">
      <div className="max-w-4xl mx-auto px-6 py-10">

        {/* Header */}
        <div className="mb-8 flex items-end justify-between gap-6 flex-wrap">
          <div>
            <p className="text-xs font-semibold uppercase tracking-widest text-indigo-500 mb-1">Portfolio Creation</p>
            <h1 className="text-3xl font-bold text-slate-800">{data.developer}</h1>
            <div className="flex gap-2 flex-wrap mt-3">
              {data.coreCompetencies.map(c => (
                <span key={c} className="text-xs font-semibold px-3 py-1 rounded-full bg-indigo-100 text-indigo-700">
                  {c}
                </span>
              ))}
            </div>
          </div>
          <div className="text-right">
            <p className="text-5xl font-bold text-indigo-600 leading-none">{data.projects.length}</p>
            <p className="text-xs font-semibold uppercase tracking-widest text-slate-400 mt-1">Projects</p>
          </div>
        </div>

        {/* Projects section */}
        <div className="mb-10">
          <p className="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-4 flex items-center gap-2">
            <span className="inline-block w-5 h-0.5 bg-indigo-400 rounded" />
            Projects
          </p>
          <div className="space-y-4">
            {data.projects.map((p, i) => <ProjectCard key={p.id} project={p} index={i} />)}
          </div>
        </div>

        {/* Language Proficiency section */}
        <div className="mb-10">
          <p className="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-4 flex items-center gap-2">
            <span className="inline-block w-5 h-0.5 bg-indigo-400 rounded" />
            Language Proficiency
          </p>
          <div className="bg-white rounded-2xl border border-slate-200 px-6 py-5 flex flex-col gap-3.5">
            {data.languages.map((l, i) => <LangBar key={l.name} {...l} index={i} />)}
          </div>
        </div>

        {/* Back button */}
          <div className="flex justify-between mt-8">
            <button
              onClick={onPrevious}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-bold text-white bg-indigo-400 shadow-sm hover:bg-indigo-700 transition-all"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M19 12H5M12 19l-7-7 7-7" />
              </svg>
              Back
            </button>
          
            {/* Next button */}
            <button
              onClick={onComplete}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-bold text-white bg-indigo-400 shadow-sm hover:bg-indigo-700 transition-all"
            >
              Next
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M5 12h14M12 5l7 7-7 7" />
              </svg>
            </button>
          </div>  

        {/* Footer */}
        <p className="text-center text-xs text-slate-300 mt-4">
          Generated by ImportIQ · {new Date().getFullYear()}
        </p>


      </div>
    </div>
  );
}