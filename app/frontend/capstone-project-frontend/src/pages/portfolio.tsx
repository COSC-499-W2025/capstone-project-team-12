import { type PortfolioData } from "../types/types";
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
      name: "COSC360-project-piggybank",
      timeline: "Feb 2025 – Apr 2025",
      duration: "41 days",
      role: "Feature Developer",
      insight: "Contributed a substantial amount of new code, indicating a strong role in implementing features and expanding the project's functionality.",
      contribution: { level: "Top Contributor", teamSize: 3, rank: 1, percentile: 66.67, share: 46.0 },
      totals: { commits: 63,  files: 362, added: 11560, deleted: 3144, net: 8416 },
      mine:   { commits: 29,  added: 6523, deleted: 2096, net: 4427, files: 162 },
      technologies: [],
    },
    {
      id: 2,
      name: "341-FarmToTableApp",
      timeline: "Apr 2025 – Apr 2025",
      duration: "3 days",
      role: "Feature Developer",
      insight: "Contributed a substantial amount of new code, indicating a strong role in implementing features and expanding the project's functionality.",
      contribution: { level: "Significant Contributor", teamSize: 4, rank: 2, percentile: 50.0, share: 15.6 },
      totals: { commits: 32,  files: 326, added: 16669, deleted: 857,  net: 15812 },
      mine:   { commits: 5,   added: 836,  deleted: 16,   net: 820,  files: 26 },
      technologies: ["android.os", "java.util", "androidx.annotation"],
    },
  ],
};

export default function DevPortfolio({ data = PORTFOLIO_DATA, onComplete, onPrevious }: {
  data?: PortfolioData;
  onComplete?: () => void;
  onPrevious?: () => void;
}) {
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

        {/* Navigation buttons */}
        <div className="flex justify-between mt-8">
          {onPrevious && (
            <button
              onClick={onPrevious}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-bold text-white bg-indigo-500 shadow-sm hover:bg-indigo-700 transition-all"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M19 12H5M12 19l-7-7 7-7" />
              </svg>
              Back
            </button>
          )}
          {onComplete && (
            <button
              onClick={onComplete}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-bold text-white bg-indigo-600 shadow-sm hover:bg-indigo-700 transition-all ml-auto"
            >
              Next
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M5 12h14M12 5l7 7-7 7" />
              </svg>
            </button>
          )}
        </div>

        {/* Footer */}
        <p className="text-center text-xs text-slate-300 mt-8">
          Generated by ImportIQ · {new Date().getFullYear()}
        </p>

      </div>
    </div>
  );
}