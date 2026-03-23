import { useState, useEffect } from "react";
import { useNavigate } from 'react-router-dom';
import type { Analysis, EmptyStateProps,  ToastProps, RawProject, RawResume, RawPortfolio } from "../types/dashboardTypes";
import { AnalysisCard } from "../components/analysisCard";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8080";


// Mapping function

function mapProject(
  p: RawProject,
  resumes: RawResume[],
  portfolios: RawPortfolio[]
): Analysis {
  // Extract repo names from project_insights if available
  let repos: string[] = [];
  try {
    const insights = typeof p.project_insights === "string"
      ? JSON.parse(p.project_insights)
      : p.project_insights;
    repos = (insights?.analyzed_insights ?? []).map(
      (r: any) => r.repository_name ?? r.name ?? "Unknown"
    );
  } catch {}

  return {
    id: p.analysis_id,
    label: p.analysis_title ?? p.analysis_id,
    createdAt: p.creation_date?.slice(0, 10) ?? "",
    repos,
    resumeIds: resumes.map(r => r.resume_id),
    portfolioIds: portfolios.map(r => r.portfolio_id),
    hasResume: resumes.length > 0,
    hasPortfolio: portfolios.length > 0,
    hasInsights: true,
    status: "complete",
  };
}


export default function Dashboard() {
  const navigate = useNavigate();
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(null), 3500);
  };

  // Data fetching (projects, resumes and portfolios)
  useEffect(() => {
    async function loadDashboard() {
      try {
        const [projectsRes, resumesRes, portfoliosRes] = await Promise.all([
          fetch(`${API_BASE}/projects`),
          fetch(`${API_BASE}/resumes`),
          fetch(`${API_BASE}/portfolios`),
        ]);

        if (!projectsRes.ok) throw new Error("Failed to load projects");
        if (!resumesRes.ok)  throw new Error("Failed to load resumes");
        if (!portfoliosRes.ok) throw new Error("Failed to load portfolios");

        const [projects, allResumes, allPortfolios]: [
          RawProject[],
          RawResume[],
          RawPortfolio[]
        ] = await Promise.all([
          projectsRes.json(),
          resumesRes.json(),
          portfoliosRes.json(),
        ]);

        // Group resumes and portfolios by analysis id (doing this manually to reduce the number of api calls
        // instead of calling GET /portfolio/{analysis_id} and GET /resume/{analysis_id} for each analysis
        const resumesByAnalysis = allResumes.reduce<Record<string, RawResume[]>>(
          (acc, r) => {
            (acc[r.analysis_id] ??= []).push(r);
            return acc;
          }, {}
        );

        const portfoliosByAnalysis = allPortfolios.reduce<Record<string, RawPortfolio[]>>(
          (acc, p) => {
            (acc[p.analysis_id] ??= []).push(p);
            return acc;
          }, {}
        );

        setAnalyses(
          projects.map(p =>
            mapProject(
              p,
              resumesByAnalysis[p.analysis_id] ?? [],
              portfoliosByAnalysis[p.analysis_id] ?? []
            )
          )
        );
      } catch (err) {
        showToast(err instanceof Error ? err.message : "Failed to load dashboard.");
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);



  // ── Handlers ────────────────────────────────────────────────────────────────

  const handleDeleteAnalysis = async (id: string) => {
    try {
      const response = await fetch(`${API_BASE}/projects/${id}`, { method: "DELETE" });

      if (!response.ok) {
        throw new Error("Failed to delete analysis");
      }

      setAnalyses(function(prev) {
        return prev.filter(analysis => analysis.id !== id);
      })

      showToast("Analysis deleted.")

    } catch (error) {
      const message = error instanceof Error ? error.message : "Failed to delete analysis."
      showToast(message);
    }
  };


  const handleDeleteResume = async (resume_id: number) => {
    try {
      const response = await fetch(`${API_BASE}/resume/${resume_id}`, { method: "DELETE" });

      if (!response.ok) {
        throw new Error("Failed to delete resume.");
      }

      // resume is managed in analysis state instead of having its own
      setAnalyses(prev => prev.map(analysis => {
        if (!analysis.resumeIds.includes(resume_id)) return analysis;
        return { ...analysis, resumeIds: analysis.resumeIds.filter(id => id !== resume_id) };
      }));

      showToast("Resume deleted.")

    } catch (error) {
        const message = error instanceof Error ? error.message : "Failed to delete resume.";
        showToast(message);
    }
  };


  const handleDeletePortfolio = async (portfolio_id: number) => {
    try {
      const response = await fetch(`${API_BASE}/portfolio/${portfolio_id}`, { method: "DELETE" });

      if (!response.ok) {
        throw new Error("Failed to delete portfolio.");
      }

      // resume is managed in analysis state instead of having its own
      setAnalyses(prev => prev.map(analysis => {
        if (!analysis.portfolioIds.includes(portfolio_id)) return analysis;
        return { ...analysis, portfolioIds: analysis.portfolioIds.filter(id => id !== portfolio_id) };
      }));

      showToast("Portfolio deleted.")

    } catch (error) {
        const message = error instanceof Error ? error.message : "Failed to delete portfolio.";
        showToast(message);
    }
  };

  const handleIncremental = (id: string) => {
    navigate(`/analysis/new/import?analysisId=${id}`);
  };


  const handleViewResume = (_analysis: Analysis, resumeId: number) => navigate(`/resume/${resumeId}`);
  const handleViewPortfolio = (_analysis: Analysis, portfolioId: number) => navigate(`/portfolio/${portfolioId}`);
  const handleViewInsights  = (analysis: Analysis) => navigate(`/insights/${analysis.id}`);

  // derive counts for top stat component
  const totalResumes    = analyses.reduce((n, a) => n + a.resumeIds.length, 0);
  const totalPortfolios = analyses.reduce((n, a) => n + a.portfolioIds.length, 0);



  // ── Render ──────────────────────────────────────────────────────────────────

  return (
    <div className="min-h-screen bg-slate-50 font-sans">
      <div className="max-w-4xl mx-auto px-6 py-10">

        {/* Header */}
        <div className="mb-8 flex items-start justify-between gap-4 flex-wrap">
          <div>
            <p className="text-xs font-semibold uppercase tracking-widest text-indigo-500 mb-1">My Dashboard</p>
            <h1 className="text-3xl font-bold text-slate-800">Your analyses.</h1>
            <p className="text-sm text-slate-400 mt-1">Manage past analyses, view generated outputs, and run new ones.</p>
          </div>
          <button
            onClick={() => navigate('/analysis/new/onboarding')}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-bold text-white bg-indigo-600 shadow-sm hover:bg-indigo-700 hover:shadow-md transition-all mt-1"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
            </svg>
            New Analysis
          </button>
        </div>

        {/* Stats strip */}
        {!loading && analyses.length > 0 && (
          <div className="grid grid-cols-3 gap-3 mb-8">
            {(
              [
                { label: "Analyses",   value: analyses.length, icon: "🔍" },
                { label: "Resumes",    value: totalResumes,    icon: "📄" },
                { label: "Portfolios", value: totalPortfolios, icon: "🗂️" },
              ] as const
            ).map(({ label, value, icon }) => (
              <div key={label} className="bg-white rounded-2xl border border-slate-200 px-4 py-4 flex items-center gap-3">
                <span className="text-xl">{icon}</span>
                <div>
                  <p className="text-xl font-bold text-slate-800 leading-none">{value}</p>
                  <p className="text-xs text-slate-400 mt-0.5">{label}</p>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Analysis list */}
        {loading ? (
          <p className="text-sm text-slate-400 py-10 text-center">Loading analyses…</p>
        ) : analyses.length === 0 ? (
          <EmptyState onNew={() => navigate('/analysis/new/onboarding')} />
        ) : (
          <div className="space-y-3">
            <p className="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-1">All Analyses</p>
            {analyses.map(a => (
              <AnalysisCard
                key={a.id}
                analysis={a}
                onDelete={handleDeleteAnalysis}
                onDeleteResume={handleDeleteResume}
                onDeletePortfolio={handleDeletePortfolio}
                onIncremental={handleIncremental}
                onViewResume={handleViewResume}
                onViewPortfolio={handleViewPortfolio}
                onViewInsights={handleViewInsights}
              />
            ))}
          </div>
        )}
      </div>

      {toast !== null && <Toast message={toast} onDismiss={() => setToast(null)} />}
    </div>
  );
}



// ── Sub-components ────────────────────────────────────────────────────────────

export function EmptyState({ onNew }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center">
      <div className="w-14 h-14 rounded-2xl bg-indigo-50 flex items-center justify-center mb-4 text-2xl">📂</div>
      <p className="text-base font-bold text-slate-700 mb-1">No analyses yet</p>
      <p className="text-sm text-slate-400 mb-5">Run your first analysis to get tailored insights, a resume, and more.</p>
      <button
        onClick={onNew}
        className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-bold text-white bg-indigo-600 shadow-sm hover:bg-indigo-700 transition-all"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
        </svg>
        New Analysis
      </button>
    </div>
  );
}

function Toast({ message, onDismiss }: ToastProps) {
  return (
    <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 bg-slate-800 text-white text-sm font-semibold px-5 py-3 rounded-2xl shadow-xl flex items-center gap-3">
      {message}
      <button onClick={onDismiss} className="!bg-transparent !border-none text-slate-400 hover:text-white text-lg">×</button>
    </div>
  );
}
