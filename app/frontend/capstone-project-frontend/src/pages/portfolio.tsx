import { type PortfolioData } from "../types/types";
import { useEffect, useState, useMemo, useCallback, useRef } from "react";
import { useNavigate, useParams } from 'react-router-dom';
import ProjectCard from "../components/projectcard";
import LangBar from "../components/langbar";
import GrowthMetrics from "../components/growthMetrics";

// ─── Highlight helper ─────────────────────────────────────────────────────────
// Wraps matched substrings in <mark> spans for search highlighting.
function Highlight({ text, query }: { text: string; query: string }) {
  if (!query.trim()) return <>{text}</>;
  const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, "gi");
  const parts = text.split(regex);
  return (
    <>
      {parts.map((part, i) =>
        regex.test(part) ? (
          <mark key={i} className="bg-amber-200 text-amber-900 rounded px-0.5 font-semibold">{part}</mark>
        ) : (
          <span key={i}>{part}</span>
        )
      )}
    </>
  );
}

// Returns true if `query` matches anywhere in the project's searchable fields
function projectMatchesQuery(p: PortfolioData["projects"][number], q: string): boolean {
  if (!q.trim()) return true;
  const lower = q.toLowerCase();
  return [
    p.name, p.timeline, p.role, p.insight, p.duration,
    p.contribution.level,
    ...p.technologies,
  ].some(v => v?.toLowerCase().includes(lower));
}

function langMatchesQuery(l: { name: string }, q: string): boolean {
  if (!q.trim()) return true;
  return l.name.toLowerCase().includes(q.toLowerCase());
}

// ─── SAMPLE DATA ─────────────────────────────────────────────────────────────
const PORTFOLIO_DATA: PortfolioData = {
  title: "Portfolio Name",
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
      name: "Example-1",
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
      name: "Example-2",
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
  growthMetrics: {
    has_comparison: true,
    earliest_project: "Example-1",
    latest_project: "Example-2",
    code_metrics: {
      commit_growth: 49.2,
      file_growth: -10.1,
      lines_growth: 87.6,
      user_lines_growth: -81.5,
    },
    technology_metrics: {
      framework_growth: 50.0,
      earliest_frameworks: 2,
      latest_frameworks: 3,
    },
    testing_evolution: {
      testing_status: "",
      coverage_improvement: 0,
      earliest_has_tests: false,
      latest_has_tests: false,
    },
    collaboration_evolution: {
      earliest_team_size: 3,
      latest_team_size: 4,
      earliest_level: "Top Contributor",
      latest_level: "Significant Contributor",
      collaboration_summary: "Moved from a smaller team with high ownership to a larger collaborative team.",
    },
    role_evolution: {
      earliest_role: "Feature Developer",
      latest_role: "Feature Developer",
      role_changed: false,
    },
    framework_timeline_list: [
      {
        project_name: "Example-1",
        date_range: "Feb 2025 – Apr 2025",
        frameworks: ["PHP", "CSS", "JavaScript", "MySQL"],
        total_frameworks: 4,
      },
      {
        project_name: "Example-2",
        date_range: "Apr 2025 – Apr 2025",
        frameworks: ["android.os", "java.util", "androidx.annotation"],
        total_frameworks: 3,
      },
    ],
  },
};
// --------- ENDPOINT ---------------
const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8080";

async function fetchPortfolio(portfolioId: number): Promise<{ data: PortfolioData; raw: any }> {
  const res = await fetch(`${API_BASE}/portfolio/${portfolioId}`);
  if (!res.ok) throw new Error(`Failed to fetch portfolio: ${res.status} ${res.statusText}`);
  const json = await res.json();

  // Safe fallback if the backend returns a flat object instead of nested inside portfolio_data
  const d = json.portfolio_data ?? json;

  const normalised: PortfolioData = {
    title: json.portfolio_title ?? d.portfolio_title ?? "",
    coreCompetencies: d.skill_timeline?.high_level_skills ?? [],
    languages: (d.skill_timeline?.language_progression ?? []).map((l: any) => ({
      name: l.name, pct: l.percentage, files: l.file_count,
    })),
    projects: (d.projects_detail ?? []).map((p: any) => ({
      id: p.name, name: p.name, timeline: p.date_range,
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
        commits: p.statistics?.commits ?? 0, files: p.statistics?.files ?? 0,
        added: p.statistics?.additions ?? 0, deleted: p.statistics?.deletions ?? 0,
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
    growthMetrics: d.growth_metrics ? {
      ...d.growth_metrics,
      framework_timeline_list: d.skill_timeline?.framework_timeline_list ?? [],
    } : null,
  };
  return { data: normalised, raw: d };
}

async function putPortfolio(portfolioId: number, data: PortfolioData, raw: any): Promise<void> {
  const payload = {
    ...raw,
    skill_timeline: {
      ...raw.skill_timeline,
      high_level_skills: data.coreCompetencies,
      language_progression: data.languages.map(l => ({
        name: l.name, percentage: l.pct, file_count: l.files,
      })),
    },
    projects_detail: (raw.projects_detail ?? []).map((p: any, i: number) => ({
      ...p,
      ...(data.projects[i] && {
        date_range: data.projects[i].timeline,
        user_role: { role: data.projects[i].role, blurb: data.projects[i].insight },
        statistics: {
          ...p.statistics,
          commits: data.projects[i].totals.commits,
          files: data.projects[i].totals.files,
          additions: data.projects[i].totals.added,
          net_lines: data.projects[i].totals.net,
          user_commits: data.projects[i].mine.commits,
          user_lines_added: data.projects[i].mine.added,
          user_net_lines: data.projects[i].mine.net,
          user_files_modified: data.projects[i].mine.files,
        },
        frameworks_summary: { ...p.frameworks_summary, top_frameworks: data.projects[i].technologies },
      }),
    })),
  };
  const res = await fetch(`${API_BASE}/portfolio/${portfolioId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ portfolio_title: data.title, portfolio_data: payload }),
  });
  if (!res.ok) throw new Error(`Failed to update portfolio: ${res.status} ${res.statusText}`);
}

// ─── Edit primitives ──────────────────────────────────────────────────────────
const inputCls = "w-full border border-[#eef0f6] rounded-lg px-3 py-1.5 text-sm text-[#0f1629] bg-[#eef0f6] focus:outline-none focus:ring-2 focus:ring-[#6378ff]/30 focus:border-[#6378ff]/50 transition-all font-sans placeholder:text-[#9ca3af]";

function Field({ value, onChange, placeholder, multiline = false, rows = 2, className = "" }: {
  value: string; onChange: (v: string) => void; placeholder?: string;
  multiline?: boolean; rows?: number; className?: string;
}) {
  const cls = `${inputCls} ${className}`;
  return multiline
    ? <textarea value={value} onChange={e => onChange(e.target.value)} placeholder={placeholder} rows={rows} className={`${cls} resize-none`} />
    : <input type="text" value={value} onChange={e => onChange(e.target.value)} placeholder={placeholder} className={cls} />;
}

function NumberField({ value, onChange, className = "" }: {
  value: number; onChange: (v: number) => void; className?: string;
}) {
  return (
    <input
      type="text" inputMode="numeric" defaultValue={value} key={value}
      onChange={e => { if (!/^\d*$/.test(e.target.value)) e.target.value = e.target.value.replace(/\D/g, ""); }}
      onBlur={e => onChange(parseInt(e.target.value) || 0)}
      className={`${inputCls} ${className}`}
    />
  );
}

function EditControls({ editing, onEdit, onSave, onCancel, saving = false, label }: {
  editing: boolean; onEdit: () => void; onSave: () => void; onCancel: () => void; saving?: boolean; label: string;
}) {
  if (!editing) return (
    <button onClick={onEdit} aria-label={`Edit ${label}`} className="text-[11px] font-bold tracking-[0.08em] uppercase text-[#6378ff] border border-[#6378ff]/25 rounded-lg px-3 py-1 hover:bg-[#6378ff]/5 transition-all">
      Edit
    </button>
  );
  return (
    <div className="flex gap-2">
      <button onClick={onSave} disabled={saving} aria-label={`Save ${label}`} className="text-[11px] font-bold tracking-[0.08em] uppercase text-white bg-[#6378ff] rounded-lg px-3 py-1 hover:bg-[#4f63e7] transition-all disabled:opacity-50">
        {saving ? "Saving…" : "Save"}
      </button>
      <button onClick={onCancel} aria-label={`Cancel ${label}`} className="text-[11px] font-bold tracking-[0.08em] uppercase text-[#64748b] border border-slate-200 rounded-lg px-3 py-1 hover:bg-slate-50 transition-all">
        Cancel
      </button>
    </div>
  );
}

function useEditState<T>(value: T) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState<T>(value);
  const open   = () => { setDraft(value); setEditing(true); };
  const cancel = () => { setDraft(value); setEditing(false); };
  return { editing, draft, setDraft, open, cancel, close: () => setEditing(false) };
}

function TagChip({ label, onRemove }: { label: string; onRemove?: () => void }) {
  return (
    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-indigo-100 text-indigo-700">
      {label}
      {onRemove && <button onClick={onRemove} className="text-indigo-300 hover:text-indigo-500 text-base leading-none ml-0.5 bg-transparent border-none">×</button>}
    </span>
  );
}

function AddTag({ placeholder, onAdd }: { placeholder: string; onAdd: (v: string) => void }) {
  const [val, setVal] = useState("");
  const commit = () => { if (val.trim()) { onAdd(val.trim()); setVal(""); } };
  return (
    <div className="flex gap-2 mt-2">
      <input value={val} onChange={e => setVal(e.target.value)} onKeyDown={e => e.key === "Enter" && commit()} placeholder={placeholder} className={inputCls} />
      <button onClick={commit} className="text-[11px] font-bold tracking-[0.08em] uppercase text-white bg-[#6378ff] rounded-lg px-3 py-1 hover:bg-[#4f63e7] transition-all whitespace-nowrap">+ Add</button>
    </div>
  );
}

function AddLanguageRow({ onAdd }: { onAdd: (name: string, files: number) => void }) {
  const [name, setName] = useState("");
  const [files, setFiles] = useState("0");
  const commit = () => { if (name.trim()) { onAdd(name.trim(), parseInt(files) || 0); setName(""); setFiles("0"); } };
  return (
    <div className="flex gap-2 mt-2">
      <input value={name} onChange={e => setName(e.target.value)} onKeyDown={e => e.key === "Enter" && commit()} placeholder="Language name…" className={inputCls} />
      <input type="text" inputMode="numeric" value={files} onChange={e => { if (/^\d*$/.test(e.target.value)) setFiles(e.target.value); }} placeholder="Files" className={`${inputCls} w-20`} />
      <button onClick={commit} className="text-[11px] font-bold tracking-[0.08em] uppercase text-white bg-[#6378ff] rounded-lg px-3 py-1 hover:bg-[#4f63e7] transition-all whitespace-nowrap">+ Add</button>
    </div>
  );
}

// ─── Public mode: Search bar ──────────────────────────────────────────────────
function SearchBar({ query, onChange }: { query: string; onChange: (v: string) => void }) {
  return (
    <div className="relative w-full">
      <svg className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" />
      </svg>
      <input
        type="text"
        value={query}
        onChange={e => onChange(e.target.value)}
        placeholder="Search projects, languages, roles…"
        className="w-full pl-8 pr-8 py-1.5 text-sm rounded-lg border border-slate-200 bg-white focus:outline-none focus:ring-2 focus:ring-[#6378ff]/30 focus:border-[#6378ff]/50 transition-all placeholder:text-slate-400"
      />
      {query && (
        <button onClick={() => onChange("")} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-300 hover:text-slate-500 transition-colors text-lg leading-none bg-transparent border-none">×</button>
      )}
    </div>
  );
}

// ─── Public mode: Filter chips ────────────────────────────────────────────────
type FilterState = {
  projects: Record<string | number, boolean>; // keyed by project id
  showLanguageProficiency: boolean;
  showSkillsTimeline: boolean;
  showGrowth: boolean;
};

function FilterBar({
  projects,
  filters,
  onChange,
}: {
  projects: PortfolioData["projects"];
  filters: FilterState;
  onChange: (f: FilterState) => void;
}) {
  const chipCls = (active: boolean) =>
    `inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border transition-all cursor-pointer select-none ${
      active
        ? "bg-[#6378ff] border-[#6378ff] text-white shadow-sm"
        : "bg-white border-slate-200 text-slate-500 hover:border-[#6378ff]/40 hover:text-[#6378ff]"
    }`;

  const toggleProject = (id: string | number) =>
    onChange({ ...filters, projects: { ...filters.projects, [id]: !filters.projects[id] } });

  return (
    <div className="flex items-center gap-2 flex-wrap">
      <span className="text-[10px] font-bold tracking-widest uppercase text-slate-400 shrink-0">Filter</span>
      {projects.map(p => (
        <button key={p.id} onClick={() => toggleProject(p.id)} className={chipCls(filters.projects[p.id])}>
          {filters.projects[p.id] ? (
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><path d="M20 6 9 17l-5-5" /></svg>
          ) : (
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M3 6h18M6 6V4h12v2M19 6l-1 14H6L5 6" /></svg>
          )}
          {p.name}
        </button>
      ))}
      <div className="w-px h-4 bg-slate-200 mx-1 shrink-0" />
      <button onClick={() => onChange({ ...filters, showLanguageProficiency: !filters.showLanguageProficiency })} className={chipCls(filters.showLanguageProficiency)}>
        {filters.showLanguageProficiency && <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><path d="M20 6 9 17l-5-5" /></svg>}
        Language Proficiency
      </button>
      <button onClick={() => onChange({ ...filters, showSkillsTimeline: !filters.showSkillsTimeline })} className={chipCls(filters.showSkillsTimeline)}>
        {filters.showSkillsTimeline && <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><path d="M20 6 9 17l-5-5" /></svg>}
        Skills Timeline
      </button>
      <button onClick={() => onChange({ ...filters, showGrowth: !filters.showGrowth })} className={chipCls(filters.showGrowth)}>
        {filters.showGrowth && <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><path d="M20 6 9 17l-5-5" /></svg>}
        Growth & Evolution
      </button>
    </div>
  );
}

// ─── Mode toggle pill ─────────────────────────────────────────────────────────
function ModeToggle({ isPublic, onToggle }: { isPublic: boolean; onToggle: () => void }) {
  return (
    <button
      onClick={onToggle}
      className={`flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-bold tracking-wide border transition-all duration-200 ${
        isPublic
          ? "bg-emerald-50 border-emerald-200 text-emerald-700 hover:bg-emerald-100"
          : "bg-slate-100 border-slate-200 text-slate-600 hover:bg-slate-200"
      }`}
      title={isPublic ? "Switch to Private (editing enabled)" : "Switch to Public (read-only view)"}
    >
      {isPublic ? (
        <>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10" /><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
          </svg>
          Public
        </>
      ) : (
        <>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <rect width="18" height="11" x="3" y="11" rx="2" ry="2" /><path d="M7 11V7a5 5 0 0 1 10 0v4" />
          </svg>
          Private
        </>
      )}
    </button>
  );
}

// ─── Navbar ───────────────────────────────────────────────────────────────────
function Navbar({
  isPublic,
  onToggleMode,
  searchQuery,
  onSearchChange,
  projects,
  filters,
  onFiltersChange,
}: {
  isPublic: boolean;
  onToggleMode: () => void;
  searchQuery: string;
  onSearchChange: (v: string) => void;
  projects: PortfolioData["projects"];
  filters: FilterState;
  onFiltersChange: (f: FilterState) => void;
}) {
  const [visible, setVisible] = useState(true);
  const lastY = useRef(0);

  useEffect(() => {
    const onScroll = () => {
      const currentY = window.scrollY;
      // Show when scrolling up or near the top; hide when scrolling down
      setVisible(currentY < lastY.current || currentY < 10);
      lastY.current = currentY;
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <div
      className={`sticky top-0 z-30 border-b transition-all duration-300 ${
        isPublic ? "bg-white/95 border-slate-100" : "bg-slate-50/95 border-slate-200"
      } backdrop-blur-sm ${visible ? "translate-y-0 opacity-100" : "-translate-y-full opacity-0"}`}
    >
      <div className="max-w-4xl mx-auto px-6">
        {/* Top row: search (public) or empty left + mode toggle */}
        <div className="flex items-center justify-between py-2.5 gap-4">
          <div className="flex-1">
            {isPublic && <SearchBar query={searchQuery} onChange={onSearchChange} />}
          </div>
          <ModeToggle isPublic={isPublic} onToggle={onToggleMode} />
        </div>
        {/* Filter row — public mode only */}
        {isPublic && (
          <div className="pb-2.5">
            <FilterBar projects={projects} filters={filters} onChange={onFiltersChange} />
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Editable section: Projects ───────────────────────────────────────────────
function ProjectsSection({
  projects,
  onChange,
  saving,
  isPublic,
  searchQuery,
  visibleProjectIds,
}: {
  projects: PortfolioData["projects"];
  onChange: (projects: PortfolioData["projects"]) => void;
  saving: boolean;
  isPublic: boolean;
  searchQuery: string;
  visibleProjectIds: Set<string | number>;
}) {
  const [editingIdx, setEditingIdx] = useState<number | null>(null);
  const [draft, setDraft] = useState<PortfolioData["projects"][number] | null>(null);

  const save = (i: number) => {
    if (!draft) return;
    const next = [...projects]; next[i] = draft;
    onChange(next); setEditingIdx(null); setDraft(null);
  };
  const cancel = () => { setEditingIdx(null); setDraft(null); };

  // In public mode, apply search + filter. In private, show all.
  const visibleProjects = useMemo(() => {
    if (!isPublic) return projects.map((p, i) => ({ p, i }));
    return projects
      .map((p, i) => ({ p, i }))
      .filter(({ p }) => visibleProjectIds.has(p.id) && projectMatchesQuery(p, searchQuery));
  }, [projects, isPublic, visibleProjectIds, searchQuery]);

  return (
    <div className="mb-10">
      <p className="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-4 flex items-center gap-2">
        <span className="inline-block w-5 h-0.5 bg-indigo-400 rounded" />Projects
        {isPublic && visibleProjects.length !== projects.length && (
          <span className="text-[10px] font-semibold text-slate-300 normal-case tracking-normal">
            — showing {visibleProjects.length} of {projects.length}
          </span>
        )}
      </p>

      {visibleProjects.length === 0 ? (
        <div className="bg-white rounded-2xl border border-dashed border-slate-200 px-6 py-10 text-center">
          <p className="text-sm text-slate-400">No projects match your search or filters.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {visibleProjects.map(({ p, i }) => (
            <div key={p.id}>
              {!isPublic && editingIdx === i && draft ? (
                <div className="bg-white border border-[#6378ff]/20 rounded-2xl p-5 space-y-5">
                  <div className="space-y-3">
                    <div>
                      <p className="text-[11px] font-bold tracking-[0.1em] uppercase text-[#64748b] mb-1.5">Project Name</p>
                      <Field value={draft.name} onChange={v => setDraft(d => d && ({ ...d, name: v }))} placeholder="Project name" />
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <p className="text-[11px] font-bold tracking-[0.1em] uppercase text-[#64748b] mb-1.5">Timeline</p>
                        <Field value={draft.timeline} onChange={v => setDraft(d => d && ({ ...d, timeline: v }))} placeholder="e.g. Jan 2025 – Apr 2025" />
                      </div>
                      <div>
                        <p className="text-[11px] font-bold tracking-[0.1em] uppercase text-[#64748b] mb-1.5">Role</p>
                        <Field value={draft.role} onChange={v => setDraft(d => d && ({ ...d, role: v }))} placeholder="e.g. Feature Developer" />
                      </div>
                    </div>
                    <div>
                      <p className="text-[11px] font-bold tracking-[0.1em] uppercase text-[#64748b] mb-1.5">Contribution Insight</p>
                      <Field value={draft.insight} onChange={v => setDraft(d => d && ({ ...d, insight: v }))} placeholder="Describe your contribution…" multiline rows={3} />
                    </div>
                  </div>
                  <div>
                    <p className="text-[11px] font-bold tracking-[0.1em] uppercase text-[#64748b] mb-2">My Contribution</p>
                    <div className="grid grid-cols-3 gap-3">
                      <div>
                        <p className="text-[10px] font-bold tracking-widest uppercase text-[#9ca3af] mb-1">Commits</p>
                        <NumberField value={draft.mine.commits} onChange={v => setDraft(d => d && ({ ...d, mine: { ...d.mine, commits: v } }))} />
                      </div>
                      <div>
                        <p className="text-[10px] font-bold tracking-widest uppercase text-[#9ca3af] mb-1">Lines Added</p>
                        <NumberField value={draft.mine.added} onChange={v => setDraft(d => d && ({ ...d, mine: { ...d.mine, added: v, net: v - (d.mine.deleted ?? 0) } }))} />
                      </div>
                      <div>
                        <p className="text-[10px] font-bold tracking-widest uppercase text-[#9ca3af] mb-1">Files Touched</p>
                        <NumberField value={draft.mine.files} onChange={v => setDraft(d => d && ({ ...d, mine: { ...d.mine, files: v } }))} />
                      </div>
                    </div>
                  </div>
                  <div>
                    <p className="text-[11px] font-bold tracking-[0.1em] uppercase text-[#64748b] mb-2">Project Totals</p>
                    <div className="grid grid-cols-3 gap-3">
                      <div>
                        <p className="text-[10px] font-bold tracking-widest uppercase text-[#9ca3af] mb-1">Commits</p>
                        <NumberField value={draft.totals.commits} onChange={v => setDraft(d => d && ({ ...d, totals: { ...d.totals, commits: v } }))} />
                      </div>
                      <div>
                        <p className="text-[10px] font-bold tracking-widest uppercase text-[#9ca3af] mb-1">Lines Added</p>
                        <NumberField value={draft.totals.added} onChange={v => setDraft(d => d && ({ ...d, totals: { ...d.totals, added: v, net: v - (d.totals.deleted ?? 0) } }))} />
                      </div>
                      <div>
                        <p className="text-[10px] font-bold tracking-widest uppercase text-[#9ca3af] mb-1">Files Touched</p>
                        <NumberField value={draft.totals.files} onChange={v => setDraft(d => d && ({ ...d, totals: { ...d.totals, files: v } }))} />
                      </div>
                    </div>
                  </div>
                  <div>
                    <p className="text-[11px] font-bold tracking-[0.1em] uppercase text-[#64748b] mb-2">Technologies</p>
                    <div className="flex flex-wrap gap-1.5 mb-1">
                      {draft.technologies.map(t => (
                        <TagChip key={t} label={t} onRemove={() => setDraft(d => d && ({ ...d, technologies: d.technologies.filter(x => x !== t) }))} />
                      ))}
                    </div>
                    <AddTag placeholder="Add technology…" onAdd={v => { if (!draft.technologies.includes(v)) setDraft(d => d && ({ ...d, technologies: [...d.technologies, v] })); }} />
                  </div>
                  <div className="flex justify-end pt-1">
                    <EditControls editing onEdit={() => {}} onSave={() => save(i)} onCancel={cancel} saving={saving} label={`project ${i}`} />
                  </div>
                </div>
              ) : (
                <ProjectCard
                  project={p}
                  index={i}
                  onEdit={isPublic ? undefined : () => { setDraft({ ...p }); setEditingIdx(i); }}
                  searchQuery={isPublic ? searchQuery : undefined}
                />
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ─── Main component ───────────────────────────────────────────────────────────
export default function DevPortfolio({
  onComplete,
  onPrevious,
  portfolioId,
  onSidebarCollapse,
  viewMode = 'pipeline'
}: {
  onComplete?: () => void;
  onPrevious?: () => void;
  portfolioId?: number | null;
  /** Called whenever public mode changes so the parent can collapse/restore the sidebar */
  onSidebarCollapse?: (collapsed: boolean) => void;
  viewMode?: 'pipeline' | 'standalone';
}) {
    
  const navigate = useNavigate();
  const params = useParams();
  const routePortfolioId = params.id ? parseInt(params.id, 10) : null;
  const resolvedPortfolioId = portfolioId ?? (Number.isNaN(routePortfolioId) ? null : routePortfolioId);

  const [data,       setData]       = useState<PortfolioData | null>(portfolioId == null ? PORTFOLIO_DATA : null);
  const [raw,        setRaw]        = useState<any>(null);
  const [loading,    setLoading]    = useState(portfolioId != null);
  const [error,      setError]      = useState<string | null>(null);
  const [saving,     setSaving]     = useState(false);
  const [isPublic,   setIsPublic]   = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  // Initialise filter state once data is available
  const buildDefaultFilters = useCallback((d: PortfolioData): FilterState => ({
    projects: Object.fromEntries(d.projects.map(p => [p.id, true])),
    showLanguageProficiency: true,
    showSkillsTimeline: true,
    showGrowth: true,
  }), []);

  const [filters, setFilters] = useState<FilterState>({
    projects: {},
    showLanguageProficiency: true,
    showSkillsTimeline: true,
    showGrowth: true,
  });

  useEffect(() => {
    if (portfolioId == null) {
      setFilters(buildDefaultFilters(PORTFOLIO_DATA));
      return;
    }
    fetchPortfolio(portfolioId)
      .then(({ data, raw }) => {
        setData(data);
        setRaw(raw);
        setFilters(buildDefaultFilters(data));
        setLoading(false);
      })
      .catch(e => { setError(e.message); setLoading(false); });
  }, [portfolioId, buildDefaultFilters]);

  // Notify parent whenever mode changes so it can collapse the sidebar
  const toggleMode = useCallback(() => {
    const next = !isPublic;
    setIsPublic(next);
    onSidebarCollapse?.(next);
    if (!next) setSearchQuery(""); // clear search when returning to private
  }, [isPublic, onSidebarCollapse]);
    
  useEffect(() => {
    if (resolvedPortfolioId == null) return;
    fetchPortfolio(resolvedPortfolioId)
      .then(({ data, raw }) => { setData(data); setRaw(raw); setLoading(false); })
      .catch(e => { setError(e.message); setLoading(false); });
  }, [resolvedPortfolioId]);

  const update = async (patch: Partial<PortfolioData>) => {
    if (!data) return;
    const next = { ...data, ...patch };
    setData(next);
    if (resolvedPortfolioId == null) return;
    setSaving(true);
    try   { await putPortfolio(resolvedPortfolioId, next, raw); }
    catch (e) { setError(e instanceof Error ? e.message : "Save failed"); }
    finally   { setSaving(false); }
  };

  const headerEdit = useEditState(
    data ? { title: data.title, coreCompetencies: data.coreCompetencies } : { title: "", coreCompetencies: [] }
  );
  const langEdit = useEditState(data?.languages ?? []);

  const visibleLanguages = useMemo(() => {
    if (!data) return [];
    const pool = langEdit.editing ? langEdit.draft : data.languages;
    if (!isPublic) return pool;
    return pool.filter(l => langMatchesQuery(l, searchQuery));
  }, [data, langEdit.editing, langEdit.draft, isPublic, searchQuery]);

  const visibleProjectIds = useMemo(() => {
    if (!data) return new Set<string | number>();
    return new Set(data.projects.filter(p => filters.projects[p.id]).map(p => p.id));
  }, [data, filters.projects]);

  if (loading) return <div className="min-h-screen bg-slate-50 flex items-center justify-center"><p className="text-sm text-slate-400">Loading portfolio…</p></div>;
  if (error)   return <div className="min-h-screen bg-slate-50 flex items-center justify-center"><p className="text-red-500">Error: {error}</p></div>;
  if (!data)   return null;

  return (
    <div className={`min-h-screen font-sans transition-colors duration-300 ${isPublic ? "bg-white" : "bg-slate-50"}`}>
      {/* ── Sticky navbar ── */}
      <Navbar
        isPublic={isPublic}
        onToggleMode={toggleMode}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        projects={data.projects}
        filters={filters}
        onFiltersChange={setFilters}
      />

      <div className="max-w-4xl mx-auto px-6 py-10">
        {saving && <p className="text-xs text-[#6378ff] mb-3 font-semibold">Saving…</p>}

        {/* ── Header ── */}
        <div className="mb-8 flex items-end justify-between gap-6 flex-wrap">
          <div className="flex-1">
            <p className="text-xs font-semibold uppercase tracking-widest text-indigo-500 mb-1">Portfolio Creation</p>
            {!isPublic && headerEdit.editing ? (
              <div className="space-y-3">
                <div>
                  <p className="text-[11px] font-bold tracking-[0.1em] uppercase text-[#64748b] mb-1.5">Name</p>
                  <Field value={headerEdit.draft.title} onChange={v => headerEdit.setDraft(d => ({ ...d, title: v }))} placeholder="Enter Portfolio name" />
                </div>
                <div>
                  <p className="text-[11px] font-bold tracking-[0.1em] uppercase text-[#64748b] mb-2">Core Competencies</p>
                  <div className="flex gap-2 flex-wrap mb-1">
                    {headerEdit.draft.coreCompetencies.map(c => (
                      <TagChip key={c} label={c} onRemove={() => headerEdit.setDraft(d => ({ ...d, coreCompetencies: d.coreCompetencies.filter(x => x !== c) }))} />
                    ))}
                  </div>
                  <AddTag placeholder="Add competency…" onAdd={v => { if (!headerEdit.draft.coreCompetencies.includes(v)) headerEdit.setDraft(d => ({ ...d, coreCompetencies: [...d.coreCompetencies, v] })); }} />
                </div>
                <div className="flex justify-end pt-1">
                  <EditControls
                    editing
                    onEdit={headerEdit.open}
                    onSave={() => { update({ title: headerEdit.draft.title, coreCompetencies: headerEdit.draft.coreCompetencies }); headerEdit.close(); }}
                    onCancel={headerEdit.cancel}
                    saving={saving}
                    label="header"
                  />
                </div>
              </div>
            ) : (
              <>
                <div className="flex items-center gap-3">
                  <h1 className="text-3xl font-bold text-slate-800">
                    <Highlight text={data.title || "Untitled Portfolio"} query={isPublic ? searchQuery : ""} />
                  </h1>
                  {!isPublic && (
                    <EditControls editing={false} onEdit={headerEdit.open} onSave={() => {}} onCancel={headerEdit.cancel} label="header" />
                  )}
                </div>
                <div className="flex gap-2 flex-wrap mt-3">
                  {data.coreCompetencies.map(c => (
                    <span key={c} className="text-xs font-semibold px-3 py-1 rounded-full bg-indigo-100 text-indigo-700">
                      <Highlight text={c} query={isPublic ? searchQuery : ""} />
                    </span>
                  ))}
                </div>
              </>
            )}
          </div>
          {(isPublic || !headerEdit.editing) && (
            <div className="text-right">
              <p className="text-5xl font-bold text-indigo-600 leading-none">
                {isPublic
                  ? data.projects.filter(p => visibleProjectIds.has(p.id) && projectMatchesQuery(p, searchQuery)).length
                  : data.projects.length}
              </p>
              <p className="text-xs font-semibold uppercase tracking-widest text-slate-400 mt-1">Projects</p>
            </div>
          )}
        </div>

        {/* ── Projects ── */}
        <ProjectsSection
          projects={data.projects}
          onChange={projects => update({ projects })}
          saving={saving}
          isPublic={isPublic}
          searchQuery={searchQuery}
          visibleProjectIds={visibleProjectIds}
        />

        {/* ── Language Proficiency ── */}
        {(!isPublic || filters.showLanguageProficiency) && (
          <div className="mb-10">
            <div className="flex items-center justify-between mb-4">
              <p className="text-xs font-semibold uppercase tracking-widest text-slate-400 flex items-center gap-2">
                <span className="inline-block w-5 h-0.5 bg-indigo-400 rounded" />Language Proficiency
                {isPublic && searchQuery && visibleLanguages.length !== data.languages.length && (
                  <span className="text-[10px] font-semibold text-slate-300 normal-case tracking-normal">
                    — {visibleLanguages.length} match
                  </span>
                )}
              </p>
              {!isPublic && (
                <EditControls
                  editing={langEdit.editing}
                  onEdit={langEdit.open}
                  onSave={() => { update({ languages: langEdit.draft }); langEdit.close(); }}
                  onCancel={langEdit.cancel}
                  saving={saving}
                  label="languages"
                />
              )}
            </div>
            <div className="bg-white rounded-2xl border border-slate-200 px-6 py-5 flex flex-col gap-3.5">
              {visibleLanguages.length === 0 ? (
                <p className="text-sm text-slate-400 text-center py-4">No languages match your search.</p>
              ) : (
                visibleLanguages.map((l, i) => (
                  <div key={l.name} className="flex items-center gap-3">
                    <div className="flex-1">
                      <LangBar
                        {...l}
                        index={i}
                        // Pass search query for LangBar to highlight the name if it supports it.
                        // If LangBar doesn't accept searchQuery, the Highlight component below
                        // serves as a graceful fallback shown beside/over the bar.
                      />
                    </div>
                    {!isPublic && langEdit.editing && (
                      <>
                        <NumberField value={l.files} onChange={v => langEdit.setDraft(d => d.map(x => x.name === l.name ? { ...x, files: v } : x))} className="w-20" />
                        <p className="text-[10px] text-[#9ca3af] whitespace-nowrap shrink-0">files</p>
                        <button onClick={() => langEdit.setDraft(d => d.filter(x => x.name !== l.name))} className="text-[#c4c9d4] hover:text-red-400 text-xl leading-none bg-transparent border-none shrink-0 transition-colors">×</button>
                      </>
                    )}
                  </div>
                ))
              )}
              {!isPublic && langEdit.editing && (
                <div className="pt-2 border-t border-slate-100">
                  <p className="text-[11px] font-bold tracking-[0.1em] uppercase text-[#64748b] mb-1">Add Language</p>
                  <AddLanguageRow onAdd={(name, files) => { if (!langEdit.draft.map(l => l.name.toLowerCase()).includes(name.toLowerCase())) langEdit.setDraft(d => [...d, { name, pct: 0, files }]); }} />
                </div>
              )}
            </div>
          </div>
        )}

        {/* ── Skills Timeline + Growth & Evolution ── */}
        {data.growthMetrics && (!isPublic || filters.showSkillsTimeline || filters.showGrowth) && (
          <GrowthMetrics
            g={data.growthMetrics}
            showSkillsTimeline={!isPublic || filters.showSkillsTimeline}
            showGrowth={!isPublic || filters.showGrowth}
          />
        )}

        {/* ── Navigation ── */}
        {!isPublic && (
        <div className="flex justify-between mt-8">
          {viewMode === 'pipeline' ? (
            <>
              <button onClick={() => (onPrevious ? onPrevious() : navigate('/analysis/new/resume'))} className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-bold text-white bg-indigo-400 shadow-sm hover:bg-indigo-700 transition-all">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M19 12H5M12 19l-7-7 7-7" /></svg>
                Back
              </button>
              <button onClick={() => (onComplete ? onComplete() : navigate('/dashboard'))} className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-bold text-white bg-indigo-400 shadow-sm hover:bg-indigo-700 transition-all">
                Next
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14M12 5l7 7-7 7" /></svg>
              </button>
            </>
          ) : (
            <button onClick={() => navigate('/dashboard')} className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-bold text-white bg-indigo-400 shadow-sm hover:bg-indigo-700 transition-all">
              Return to Dashboard
            </button>
          )}
        </div>
        )}

        <p className="text-center text-xs text-slate-300 mt-4">
          {resolvedPortfolioId ? "" : "Preview mode · connect a portfolio ID to load real data"} · Generated by Team 12 · {new Date().getFullYear()}
        </p>
      </div>
    </div>
  );
}