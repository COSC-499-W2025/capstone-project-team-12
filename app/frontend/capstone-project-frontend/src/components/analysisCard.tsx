import { useState } from "react";
import type { BadgeColor, AnalysisCardProps, BadgeProps, IconButtonProps } from "../types/dashboardTypes";
import { Modal, IncrementalUpdateModal } from "./modals";




function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-CA", { year: "numeric", month: "short", day: "numeric" });
}


function Badge({ label, color = "indigo" }: BadgeProps) {
  const colors: Record<BadgeColor, string> = {
    indigo: "bg-indigo-100 text-indigo-700",
    emerald: "bg-emerald-100 text-emerald-700",
    slate: "bg-slate-100 text-slate-500",
    amber: "bg-amber-100 text-amber-700",
  };
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${colors[color]}`}>
      {label}
    </span>
  );
}


function IconButton({ onClick, title, className = "", children }: IconButtonProps) {
  return (
    <button
      onClick={onClick}
      title={title}
      className={`p-1.5 rounded-lg transition-all text-slate-400 hover:text-slate-700 hover:bg-slate-100 ${className}`}
    >
      {children}
    </button>
  );
}

function TrashIcon() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="3 6 5 6 21 6" />
      <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6" />
      <path d="M10 11v6" /><path d="M14 11v6" /><path d="M9 6V4h6v2" />
    </svg>
  );
}



export function AnalysisCard({
  analysis,
  onDelete,
  onDeleteResume,
  onDeletePortfolio,
  onIncremental,
  onViewResume,
  onViewPortfolio,
  onViewInsights,
}: AnalysisCardProps) {
  const [expanded, setExpanded] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [confirmDeleteResume, setConfirmDeleteResume] = useState(false);
  const [confirmDeletePortfolio, setConfirmDeletePortfolio] = useState(false);
  const [showIncremental, setShowIncremental] = useState(false);

  return (
    <>
      <div className={`bg-white rounded-2xl border transition-all duration-200 ${expanded ? "border-indigo-200 shadow-md" : "border-slate-200 hover:border-indigo-200 hover:shadow-sm"}`}>

        {/* Header row */}
        <div
          className="flex items-center justify-between gap-3 px-5 py-4 cursor-pointer select-none"
          onClick={() => setExpanded(e => !e)}
        >
          <div className="flex items-center gap-3 min-w-0">
            <div className={`w-2 h-2 rounded-full shrink-0 ${analysis.status === "complete" ? "bg-emerald-400" : "bg-amber-400"}`} />
            <div className="min-w-0">
              <p className="text-sm font-semibold text-slate-800 truncate">{analysis.label}</p>
              <p className="text-xs text-slate-400 mt-0.5">
                {formatDate(analysis.createdAt)} · {analysis.repos.length} repo{analysis.repos.length !== 1 ? "s" : ""}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            {analysis.hasResume    && <Badge label="Resume"    color="indigo"  />}
            {analysis.hasPortfolio && <Badge label="Portfolio" color="emerald" />}
            {analysis.hasInsights  && <Badge label="Insights"  color="slate"   />}
            <svg
              className={`w-4 h-4 text-slate-400 transition-transform duration-200 ${expanded ? "rotate-180" : ""}`}
              fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"
            >
              <path d="M6 9l6 6 6-6" />
            </svg>
          </div>
        </div>

        {/* Expanded body */}
        {expanded && (
          <div className="border-t border-slate-100 px-5 py-4 space-y-4">

            {/* Repos */}
            <div>
              <p className="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-2">Repositories</p>
              <div className="flex flex-wrap gap-2">
                {analysis.repos.map(r => (
                  <span key={r} className="bg-slate-100 text-slate-600 text-xs font-medium px-2.5 py-1 rounded-lg">{r}</span>
                ))}
              </div>
            </div>

            {/* Outputs */}
            <div>
              <p className="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-2">Generated Outputs</p>
              <div className="space-y-2">

                {/* Resume */}
                <div className="flex items-center justify-between gap-2 rounded-xl bg-slate-50 border border-slate-100 px-3 py-2.5">
                  <div className="flex items-center gap-2">
                    <span className="text-base">📄</span>
                    <div>
                      <p className="text-xs font-semibold text-slate-700">Resume</p>
                      {!analysis.hasResume && <p className="text-xs text-slate-400">Not generated</p>}
                    </div>
                  </div>
                  {analysis.hasResume ? (
                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => onViewResume(analysis)}
                        className="text-xs font-semibold text-indigo-600 border border-indigo-200 rounded-lg px-3 py-1 hover:bg-indigo-50 transition-all"
                      >
                        View
                      </button>
                      <IconButton onClick={() => setConfirmDeleteResume(true)} title="Delete resume">
                        <TrashIcon />
                      </IconButton>
                    </div>
                  ) : (
                    <span className="text-xs text-slate-400 italic">—</span>
                  )}
                </div>

                {/* Portfolio */}
                <div className="flex items-center justify-between gap-2 rounded-xl bg-slate-50 border border-slate-100 px-3 py-2.5">
                  <div className="flex items-center gap-2">
                    <span className="text-base">🗂️</span>
                    <div>
                      <p className="text-xs font-semibold text-slate-700">Portfolio</p>
                      {!analysis.hasPortfolio && <p className="text-xs text-slate-400">Not generated</p>}
                    </div>
                  </div>
                  {analysis.hasPortfolio ? (
                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => onViewPortfolio(analysis)}
                        className="text-xs font-semibold text-emerald-600 border border-emerald-200 rounded-lg px-3 py-1 hover:bg-emerald-50 transition-all"
                      >
                        View
                      </button>
                      <IconButton onClick={() => setConfirmDeletePortfolio(true)} title="Delete portfolio">
                        <TrashIcon />
                      </IconButton>
                    </div>
                  ) : (
                    <span className="text-xs text-slate-400 italic">—</span>
                  )}
                </div>

                {/* Skills & Insights */}
                <div className="flex items-center justify-between gap-2 rounded-xl bg-slate-50 border border-slate-100 px-3 py-2.5">
                  <div className="flex items-center gap-2">
                    <span className="text-base">📊</span>
                    <div>
                      <p className="text-xs font-semibold text-slate-700">Skills & Insights</p>
                      {!analysis.hasInsights && <p className="text-xs text-slate-400">Not generated</p>}
                    </div>
                  </div>
                  {analysis.hasInsights ? (
                    <button
                      onClick={() => onViewInsights(analysis)}
                      className="text-xs font-semibold text-slate-600 border border-slate-200 rounded-lg px-3 py-1 hover:bg-slate-100 transition-all"
                    >
                      View
                    </button>
                  ) : (
                    <span className="text-xs text-slate-400 italic">—</span>
                  )}
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center justify-between gap-2 pt-1 border-t border-slate-100">
              <button
                onClick={() => setShowIncremental(true)}
                className="flex items-center gap-1.5 text-xs font-semibold text-indigo-600 border border-indigo-200 rounded-lg px-3 py-1.5 hover:bg-indigo-50 transition-all"
              >
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
                </svg>
                Add Files / Update
              </button>
              <button
                onClick={() => setConfirmDelete(true)}
                className="flex items-center gap-1.5 text-xs font-semibold text-red-400 border border-red-100 rounded-lg px-3 py-1.5 hover:bg-red-50 transition-all"
              >
                <TrashIcon />
                Delete Analysis
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Confirm modals */}
      {confirmDelete && (
        <Modal
          title="Delete Analysis?"
          description={`This will permanently delete "${analysis.label}" and all its generated outputs (resume, portfolio, insights). This cannot be undone.`}
          confirmLabel="Delete"
          onConfirm={() => { onDelete(analysis.id); setConfirmDelete(false); }}
          onCancel={() => setConfirmDelete(false)}
        />
      )}
      {confirmDeleteResume && (
        <Modal
          title="Delete Resume?"
          description={`This will permanently delete the resume generated for "${analysis.label}".`}
          confirmLabel="Delete"
          onConfirm={() => { onDeleteResume(analysis.id); setConfirmDeleteResume(false); }}
          onCancel={() => setConfirmDeleteResume(false)}
        />
      )}
      {confirmDeletePortfolio && (
        <Modal
          title="Delete Portfolio?"
          description={`This will permanently delete the portfolio generated for "${analysis.label}".`}
          confirmLabel="Delete"
          onConfirm={() => { onDeletePortfolio(analysis.id); setConfirmDeletePortfolio(false); }}
          onCancel={() => setConfirmDeletePortfolio(false)}
        />
      )}
      {showIncremental && (
        <IncrementalUpdateModal
          analysis={analysis}
          onConfirm={(files) => { onIncremental(analysis.id, files); setShowIncremental(false); }}
          onCancel={() => setShowIncremental(false)}
        />
      )}
    </>
  );
}
