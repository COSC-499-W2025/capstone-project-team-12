
import { useState } from "react";
import type { Analysis, NewAnalysisPayload } from "../dashboardTypes";


interface ModalProps {
  title: string;
  description: string;
  confirmLabel: string;
  confirmColor?: "red" | "indigo";
  onConfirm: () => void;
  onCancel: () => void;
}

const inputCls =
  "w-full border border-slate-200 rounded-lg px-3 py-1.5 text-sm text-slate-700 bg-slate-50 focus:outline-none focus:ring-2 focus:ring-indigo-300 transition-all";

export function Modal({ title, description, confirmLabel, confirmColor = "red", onConfirm, onCancel }: ModalProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-xl border border-slate-200 w-full max-w-sm mx-4 p-6 space-y-4">
        <h2 className="text-base font-bold text-slate-800">{title}</h2>
        <p className="text-sm text-slate-500 leading-relaxed">{description}</p>
        <div className="flex gap-2 justify-end pt-1">
          <button onClick={onCancel} className="text-xs font-semibold text-slate-500 border border-slate-200 rounded-lg px-4 py-2 hover:bg-slate-50 transition-all">
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className={`text-xs font-bold text-white rounded-lg px-4 py-2 transition-all ${
              confirmColor === "red" ? "bg-red-500 hover:bg-red-600" : "bg-indigo-600 hover:bg-indigo-700"
            }`}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}

interface NewAnalysisModalProps {
  onConfirm: (payload: NewAnalysisPayload) => void;
  onCancel: () => void;
}

export function NewAnalysisModal({ onConfirm, onCancel }: NewAnalysisModalProps) {
  const [repos, setRepos] = useState<string[]>([""]);
  const [label, setLabel] = useState<string>("");

  const addRepo = () => setRepos(r => [...r, ""]);
  const updateRepo = (i: number, v: string) => setRepos(r => { const n = [...r]; n[i] = v; return n; });
  const removeRepo = (i: number) => setRepos(r => r.filter((_, idx) => idx !== i));

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-xl border border-slate-200 w-full max-w-md mx-4 p-6 space-y-4">
        <div>
          <h2 className="text-base font-bold text-slate-800">New Analysis</h2>
          <p className="text-xs text-slate-400 mt-0.5">Add one or more GitHub repositories to analyse.</p>
        </div>
        <div className="space-y-2">
          <label className="text-xs font-semibold uppercase tracking-widest text-slate-400">Label</label>
          <input
            value={label}
            onChange={e => setLabel(e.target.value)}
            placeholder="e.g. Summer 2025 Analyses"
            className={inputCls}
          />
        </div>
        <div className="space-y-2">
          <label className="text-xs font-semibold uppercase tracking-widest text-slate-400">Repositories</label>
          {repos.map((r, i) => (
            <div key={i} className="flex gap-2">
              <input
                value={r}
                onChange={e => updateRepo(i, e.target.value)}
                placeholder="github.com/username/repo"
                className={inputCls}
              />
              {repos.length > 1 && (
                <button onClick={() => removeRepo(i)} className="text-red-300 hover:text-red-400 text-lg px-1">×</button>
              )}
            </div>
          ))}
          <button onClick={addRepo} className="text-xs font-semibold text-indigo-500 border border-indigo-200 rounded-lg px-3 py-1.5 hover:bg-indigo-50 transition-all">
            + Add Repo
          </button>
        </div>
        <div className="flex gap-2 justify-end pt-1">
          <button onClick={onCancel} className="text-xs font-semibold text-slate-500 border border-slate-200 rounded-lg px-4 py-2 hover:bg-slate-50 transition-all">
            Cancel
          </button>
          <button
            onClick={() => onConfirm({ label: label || "Untitled Analysis", repos: repos.filter(Boolean) })}
            disabled={!repos.some(Boolean)}
            className="text-xs font-bold text-white bg-indigo-600 rounded-lg px-4 py-2 hover:bg-indigo-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Run Analysis
          </button>
        </div>
      </div>
    </div>
  );
}

interface IncrementalUpdateModalProps {
  analysis: Analysis;
  onConfirm: (files: string[]) => void;
  onCancel: () => void;
}

export function IncrementalUpdateModal({ analysis, onConfirm, onCancel }: IncrementalUpdateModalProps) {
  const [files, setFiles] = useState<string[]>([""]);

  const addFile = () => setFiles(f => [...f, ""]);
  const updateFile = (i: number, v: string) => setFiles(f => { const n = [...f]; n[i] = v; return n; });
  const removeFile = (i: number) => setFiles(f => f.filter((_, idx) => idx !== i));

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-xl border border-slate-200 w-full max-w-md mx-4 p-6 space-y-4">
        <div>
          <h2 className="text-base font-bold text-slate-800">Incremental Update</h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Add files or repos to <span className="font-semibold text-slate-600">{analysis.label}</span>.
          </p>
        </div>
        <div className="space-y-2">
          <label className="text-xs font-semibold uppercase tracking-widest text-slate-400">Additional Repositories / Files</label>
          {files.map((f, i) => (
            <div key={i} className="flex gap-2">
              <input
                value={f}
                onChange={e => updateFile(i, e.target.value)}
                placeholder="github.com/username/repo"
                className={inputCls}
              />
              {files.length > 1 && (
                <button onClick={() => removeFile(i)} className="text-red-300 hover:text-red-400 text-lg px-1">×</button>
              )}
            </div>
          ))}
          <button onClick={addFile} className="text-xs font-semibold text-indigo-500 border border-indigo-200 rounded-lg px-3 py-1.5 hover:bg-indigo-50 transition-all">
            + Add More
          </button>
        </div>
        <div className="flex gap-2 justify-end pt-1">
          <button onClick={onCancel} className="text-xs font-semibold text-slate-500 border border-slate-200 rounded-lg px-4 py-2 hover:bg-slate-50 transition-all">
            Cancel
          </button>
          <button
            onClick={() => onConfirm(files.filter(Boolean))}
            disabled={!files.some(Boolean)}
            className="text-xs font-bold text-white bg-indigo-600 rounded-lg px-4 py-2 hover:bg-indigo-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Run Update
          </button>
        </div>
      </div>
    </div>
  );
}