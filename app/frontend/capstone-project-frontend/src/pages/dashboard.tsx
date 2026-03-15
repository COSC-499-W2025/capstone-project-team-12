import { useState } from "react";
import type { Analysis, EmptyStateProps, NewAnalysisPayload, ToastProps } from "../types/dashboardTypes";
import { NewAnalysisModal } from "../components/modals";
import { AnalysisCard } from "../components/analysisCard";


// ─── Mock Data ────────────────────────────────────────────────────────────────

const mockAnalyses: Analysis[] = [
  {
    id: "a1b2c3",
    label: "Spring 2025 Analyses",
    createdAt: "2025-04-06",
    repos: ["COSC 360 Project", "Personal Portfolio"],
    hasResume: true,
    hasPortfolio: true,
    hasInsights: true,
    status: "complete",
  },
  {
    id: "d4e5f6",
    label: "Winter 2025 Analyses",
    createdAt: "2025-02-14",
    repos: ["Capstone Analysis Tool"],
    hasResume: true,
    hasPortfolio: false,
    hasInsights: true,
    status: "complete",
  },
  {
    id: "g7h8i9",
    label: "Fall 2024 Analyses",
    createdAt: "2024-12-01",
    repos: ["COSC 301 Assignment"],
    hasResume: false,
    hasPortfolio: false,
    hasInsights: true,
    status: "complete",
  },
];



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


export default function Dashboard() {
  const [analyses, setAnalyses] = useState<Analysis[]>(mockAnalyses);
  const [showNewModal, setShowNewModal] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(null), 3500);
  };

  const handleDelete = (id: string) => {
    setAnalyses(a => a.filter(x => x.id !== id));
    showToast("Analysis deleted.");
  };

  const handleDeleteResume = (id: string) => {
    setAnalyses(a => a.map(x => x.id === id ? { ...x, hasResume: false } : x));
    showToast("Resume deleted.");
  };

  const handleDeletePortfolio = (id: string) => {
    setAnalyses(a => a.map(x => x.id === id ? { ...x, hasPortfolio: false } : x));
    showToast("Portfolio deleted.");
  };

  const handleIncremental = (id: string, files: string[]) => {
    showToast(`Incremental update queued with ${files.length} item${files.length !== 1 ? "s" : ""}.`);
  };

  const handleNew = ({ label, repos }: NewAnalysisPayload) => {
    const newA: Analysis = {
      id: Math.random().toString(36).slice(2),
      label,
      createdAt: new Date().toISOString().slice(0, 10),
      repos,
      hasResume: false,
      hasPortfolio: false,
      hasInsights: false,
      status: "complete",
    };
    setAnalyses(a => [newA, ...a]);
    setShowNewModal(false);
    showToast("Analysis created! (Mock — no backend call.)");
  };

  const handleViewResume    = (a: Analysis) => showToast(`Navigating to resume for "${a.label}"…`);
  const handleViewPortfolio = (a: Analysis) => showToast(`Navigating to portfolio for "${a.label}"…`);
  const handleViewInsights  = (a: Analysis) => showToast(`Navigating to insights for "${a.label}"…`);

  const totalResumes    = analyses.filter(a => a.hasResume).length;
  const totalPortfolios = analyses.filter(a => a.hasPortfolio).length;

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
            onClick={() => setShowNewModal(true)}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-bold text-white bg-indigo-600 shadow-sm hover:bg-indigo-700 hover:shadow-md transition-all mt-1"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
            </svg>
            New Analysis
          </button>
        </div>

        {/* Stats strip */}
        {analyses.length > 0 && (
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
        {analyses.length === 0 ? (
          <EmptyState onNew={() => setShowNewModal(true)} />
        ) : (
          <div className="space-y-3">
            <p className="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-1">All Analyses</p>
            {analyses.map(a => (
              <AnalysisCard
                key={a.id}
                analysis={a}
                onDelete={handleDelete}
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

      {showNewModal && (
        <NewAnalysisModal
          onConfirm={handleNew}
          onCancel={() => setShowNewModal(false)}
        />
      )}

      {toast !== null && <Toast message={toast} onDismiss={() => setToast(null)} />}
    </div>
  );
}