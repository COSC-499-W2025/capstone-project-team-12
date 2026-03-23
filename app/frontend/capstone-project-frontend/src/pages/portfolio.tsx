import { type PortfolioData } from "../types/types";
import { useEffect, useState } from "react";
import ProjectCard from "../components/projectcard";
import LangBar from "../components/langbar";
import GrowthMetrics from "../components/growthMetrics";


// SAMPLE DATA
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
const API_BASE = "http://localhost:8080";

async function fetchPortfolio(portfolioId: number): Promise<{ data: PortfolioData; raw: any }> {
  const res = await fetch(`${API_BASE}/portfolio/${portfolioId}`);
  if (!res.ok) throw new Error(`Failed to fetch portfolio: ${res.status} ${res.statusText}`);
  const json = await res.json();
  const d = json.portfolio_data;

  const normalised: PortfolioData = {
    title: json.portfolio_title ?? d.result_id ?? "Portfolio Name",
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
    growthMetrics: d.growth_metrics ? {
      ...d.growth_metrics,
      framework_timeline_list: d.skill_timeline?.framework_timeline_list ?? [],
    } : null,
  };
  return { data: normalised, raw: d };
}


// Spreads the original raw blob and overlays only the edited fields,
// preserving all backend-only data (testing, full frameworks array, metadata etc).
async function putPortfolio(portfolioId: number, data: PortfolioData, raw: any): Promise<void> {
  const payload = {
    ...raw,
    skill_timeline: {
      ...raw.skill_timeline,
      high_level_skills: data.coreCompetencies,
      language_progression: data.languages.map(l => ({
        name: l.name,
        percentage: l.pct,
        file_count: l.files,
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
      type="text"
      inputMode="numeric"
      defaultValue={value}
      key={value}
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

// ─── Editable section: Projects ───────────────────────────────────────────────

function ProjectsSection({ projects, onChange, saving }: {
  projects: PortfolioData["projects"];
  onChange: (projects: PortfolioData["projects"]) => void;
  saving: boolean;
}) {
  const [editingIdx, setEditingIdx] = useState<number | null>(null);
  const [draft, setDraft] = useState<PortfolioData["projects"][number] | null>(null);

  const save = (i: number) => {
    if (!draft) return;
    const next = [...projects]; next[i] = draft;
    onChange(next); setEditingIdx(null); setDraft(null);
  };
  const cancel = () => { setEditingIdx(null); setDraft(null); };

  return (
    <div className="mb-10">
      <p className="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-4 flex items-center gap-2">
        <span className="inline-block w-5 h-0.5 bg-indigo-400 rounded" />Projects
      </p>
      <div className="space-y-4">
        {projects.map((p, i) => (
          <div key={p.id}>
            {editingIdx === i && draft ? (
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
              <ProjectCard project={p} index={i} onEdit={() => { setDraft({ ...p }); setEditingIdx(i); }} />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Main component ───────────────────────────────────────────────────────────

export default function DevPortfolio({ onComplete, onPrevious, portfolioId }: {
  onComplete?: () => void;
  onPrevious?: () => void;
  portfolioId?: number | null;
}) {
  const [data,    setData]    = useState<PortfolioData | null>(portfolioId == null ? PORTFOLIO_DATA : null);
  const [raw,     setRaw]     = useState<any>(null);
  const [loading, setLoading] = useState(portfolioId != null);
  const [error,   setError]   = useState<string | null>(null);
  const [saving,  setSaving]  = useState(false);

  useEffect(() => {
    if (portfolioId == null) return;
    fetchPortfolio(portfolioId)
      .then(({ data, raw }) => { setData(data); setRaw(raw); setLoading(false); })
      .catch(e => { setError(e.message); setLoading(false); });
  }, [portfolioId]);

  const update = async (patch: Partial<PortfolioData>) => {
    if (!data) return;
    const next = { ...data, ...patch };
    setData(next);
    if (portfolioId == null) return;
    setSaving(true);
    try   { await putPortfolio(portfolioId, next, raw); }
    catch (e) { setError(e instanceof Error ? e.message : "Save failed"); }
    finally   { setSaving(false); }
  };

  const headerEdit = useEditState(
    data ? { title: data.title, coreCompetencies: data.coreCompetencies } : { title: "", coreCompetencies: [] }
  );
  const langEdit = useEditState(data?.languages ?? []);

  if (loading) return <div className="min-h-screen bg-slate-50 flex items-center justify-center"><p className="text-sm text-slate-400">Loading portfolio…</p></div>;
  if (error)   return <div className="min-h-screen bg-slate-50 flex items-center justify-center"><p className="text-red-500">Error: {error}</p></div>;
  if (!data)   return null;

  return (
    <div className="min-h-screen bg-slate-50 font-sans">
      <div className="max-w-4xl mx-auto px-6 py-10">

        {saving && <p className="text-xs text-[#6378ff] mb-3 font-semibold">Saving…</p>}

        {/* Header — editable */}
        <div className="mb-8 flex items-end justify-between gap-6 flex-wrap">
          <div className="flex-1">
            <p className="text-xs font-semibold uppercase tracking-widest text-indigo-500 mb-1">Portfolio Creation</p>
            {headerEdit.editing ? (
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
                  <EditControls editing onEdit={headerEdit.open} onSave={() => { update({ title: headerEdit.draft.title, coreCompetencies: headerEdit.draft.coreCompetencies }); headerEdit.close(); }} onCancel={headerEdit.cancel} saving={saving} label="header" />
                </div>
              </div>
            ) : (
              <>
                <div className="flex items-center gap-3">
                  <h1 className="text-3xl font-bold text-slate-800">{data.title || "Untitled Portfolio"}</h1>
                  <EditControls editing={false} onEdit={headerEdit.open} onSave={() => {}} onCancel={headerEdit.cancel} label="header" />
                </div>
                <div className="flex gap-2 flex-wrap mt-3">
                  {data.coreCompetencies.map(c => (
                    <span key={c} className="text-xs font-semibold px-3 py-1 rounded-full bg-indigo-100 text-indigo-700">{c}</span>
                  ))}
                </div>
              </>
            )}
          </div>
          {!headerEdit.editing && (
            <div className="text-right">
              <p className="text-5xl font-bold text-indigo-600 leading-none">{data.projects.length}</p>
              <p className="text-xs font-semibold uppercase tracking-widest text-slate-400 mt-1">Projects</p>
            </div>
          )}
        </div>

        {/* Projects — editable */}
        <ProjectsSection projects={data.projects} onChange={projects => update({ projects })} saving={saving} />

        {/* Language Proficiency — editable */}
        <div className="mb-10">
          <div className="flex items-center justify-between mb-4">
            <p className="text-xs font-semibold uppercase tracking-widest text-slate-400 flex items-center gap-2">
              <span className="inline-block w-5 h-0.5 bg-indigo-400 rounded" />Language Proficiency
            </p>
            <EditControls editing={langEdit.editing} onEdit={langEdit.open} onSave={() => { update({ languages: langEdit.draft }); langEdit.close(); }} onCancel={langEdit.cancel} saving={saving} label="languages" />
          </div>
          <div className="bg-white rounded-2xl border border-slate-200 px-6 py-5 flex flex-col gap-3.5">
            {(langEdit.editing ? langEdit.draft : data.languages).map((l, i) => (
              <div key={l.name} className="flex items-center gap-3">
                <div className="flex-1"><LangBar {...l} index={i} /></div>
                {langEdit.editing && (
                  <>
                    <NumberField value={l.files} onChange={v => langEdit.setDraft(d => d.map(x => x.name === l.name ? { ...x, files: v } : x))} className="w-20" />
                    <p className="text-[10px] text-[#9ca3af] whitespace-nowrap shrink-0">files</p>
                    <button onClick={() => langEdit.setDraft(d => d.filter(x => x.name !== l.name))} className="text-[#c4c9d4] hover:text-red-400 text-xl leading-none bg-transparent border-none shrink-0 transition-colors">×</button>
                  </>
                )}
              </div>
            ))}
            {langEdit.editing && (
              <div className="pt-2 border-t border-slate-100">
                <p className="text-[11px] font-bold tracking-[0.1em] uppercase text-[#64748b] mb-1">Add Language</p>
                <AddLanguageRow onAdd={(name, files) => { if (!langEdit.draft.map(l => l.name.toLowerCase()).includes(name.toLowerCase())) langEdit.setDraft(d => [...d, { name, pct: 0, files }]); }} />
              </div>
            )}
          </div>
        </div>

        {/* Growth Metrics — read-only */}
        {data.growthMetrics && (
          <GrowthMetrics g={data.growthMetrics} earliestProject={data.growthMetrics.earliest_project} latestProject={data.growthMetrics.latest_project} />
        )}

        {/* Navigation */}
        <div className="flex justify-between mt-8">
          <button onClick={onPrevious} className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-bold text-white bg-indigo-400 shadow-sm hover:bg-indigo-700 transition-all">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M19 12H5M12 19l-7-7 7-7" /></svg>
            Back
          </button>
          <button onClick={onComplete} className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-bold text-white bg-indigo-400 shadow-sm hover:bg-indigo-700 transition-all">
            Next
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14M12 5l7 7-7 7" /></svg>
          </button>
        </div>

        <p className="text-center text-xs text-slate-300 mt-4">
          {portfolioId ? "Changes save automatically" : "Preview mode · connect a portfolio ID to load real data"} · Generated by ImportIQ · {new Date().getFullYear()}
        </p>

      </div>
    </div>
  );
}