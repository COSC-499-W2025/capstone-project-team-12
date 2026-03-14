import { useState } from "react";
import SectionCard from "../components/SectionCard";
import type { Resume, Project, Language } from "../types/resumeTypes";

// ─── Mock data ────────────────────────────────────────────────────────────────

const mockResume: Resume = {
  analysis_id: "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  // TODO (backend): pass github_username and user_email through _build_resume()
  github_username: "yourusername",
  user_email: "you@example.com",
  summary: "Full-stack developer with experience building collaborative web and mobile applications. Strong version control practices and a focus on clean, maintainable code.",
  projects: [
    {
      name: "Capstone Analysis Tool", date_range: "Jan 2025 - Apr 2025",
      collaboration_insight: "Contributed a substantial amount of new code, indicating a strong role in implementing features and expanding the project's functionality.",
      frameworks: ["Python", "FastAPI", "PostgreSQL", "Docker", "Flask"],
    },
    {
      name: "COSC 360 – Android App", date_range: "Apr 2025 - Present",
      collaboration_insight: "Most contributions involved modifying existing files, suggesting a maintenance-focused role aimed at improving correctness and performance.",
      frameworks: ["Java", "Android SDK", "XML", "SQLite"],
    },
    {
      name: "Personal Portfolio", date_range: "Feb 2025 - Mar 2025",
      collaboration_insight: "Balanced contribution pattern across additions, modifications, and deletions throughout the codebase.",
      frameworks: ["React", "TypeScript", "Tailwind CSS", "Vite"],
    },
  ],
  // TODO (backend): aggregate skills across all analyses, tiering needs future work
  skills: ["TypeScript", "React", "Python", "Git", "REST APIs", "Java", "Android SDK", "PostgreSQL", "Docker", "CI/CD"],
  languages: [
    { name: "TypeScript", file_count: 18 }, { name: "Java", file_count: 14 },
    { name: "Python",     file_count: 11 }, { name: "XML",  file_count: 50 },
    { name: "SQL",        file_count: 3  },
  ],
};

// ─── Primitives ───────────────────────────────────────────────────────────────

const inputCls = "w-full border border-slate-200 rounded-lg px-3 py-1.5 text-sm text-slate-700 bg-slate-50 focus:outline-none focus:ring-2 focus:ring-indigo-300 transition-all";

function Field({ value, onChange, placeholder, multiline = false, rows = 3, className = "" }: {
  value: string; onChange: (v: string) => void; placeholder?: string;
  multiline?: boolean; rows?: number; className?: string;
}) {
  const props = { value, onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => onChange(e.target.value), placeholder, className: `${inputCls} ${className}` };
  return multiline
    ? <textarea {...props} rows={rows} className={`${props.className} resize-none`} />
    : <input    {...props} type="text" />;
}

function Chip({ label, onRemove, colorClass = "bg-indigo-100 text-indigo-700" }: {
  label: string; onRemove?: () => void; colorClass?: string;
}) {
  return (
    <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold ${colorClass}`}>
      {label}
      {onRemove && <button onClick={onRemove} className="!bg-transparent !border-none text-red-300 hover:text-red-400 text-xl ml-0.5">×</button>}
    </span>
  );
}

function AddChip({ placeholder, onAdd }: { placeholder: string; onAdd: (v: string) => void }) {
  const [val, setVal] = useState("");
  const commit = () => { if (val.trim()) { onAdd(val.trim()); setVal(""); } };
  return (
    <div className="flex gap-2 mt-2">
      <input value={val} onChange={e => setVal(e.target.value)} onKeyDown={e => e.key === "Enter" && commit()}
        placeholder={placeholder} className={inputCls} />
      <button onClick={commit} className="text-xs font-bold text-white bg-indigo-600 rounded-lg px-3 py-1 hover:bg-indigo-700 transition-all">+ Add</button>
    </div>
  );
}

function EditControls({ editing, onEdit, onSave, onCancel }: {
  editing: boolean; onEdit: () => void; onSave: () => void; onCancel: () => void;
}) {
  if (!editing) return (
    <button onClick={onEdit} className="text-xs font-semibold text-indigo-500 border border-indigo-200 rounded-lg px-3 py-1 hover:bg-indigo-50 transition-all">Edit</button>
  );
  return (
    <div className="flex gap-2">
      <button onClick={onSave}   className="text-xs font-bold text-white bg-indigo-600 rounded-lg px-3 py-1 hover:bg-indigo-700 transition-all">Save</button>
      <button onClick={onCancel} className="text-xs font-semibold text-slate-500 border border-slate-200 rounded-lg px-3 py-1 hover:bg-slate-50 transition-all">Cancel</button>
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

// ─── Contact ──────────────────────────────────────────────────────────────────
// TODO (backend): pre-fill from _build_resume() once github_username and user_email are wired through

function ContactSection({ github_username, user_email, onChange }: {
  github_username: string; user_email: string;
  onChange: (u: string, e: string) => void;
}) {
  const { editing, draft, setDraft, open, cancel, close } = useEditState({ github_username, user_email });
  return (
    <SectionCard title="Contact" icon="👤">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 space-y-2">
          {editing ? (
            <>
              <Field value={draft.github_username} onChange={v => setDraft(d => ({ ...d, github_username: v }))} placeholder="GitHub username" />
              <Field value={draft.user_email}      onChange={v => setDraft(d => ({ ...d, user_email: v }))}      placeholder="Email address" />
            </>
          ) : (
            <>
              <p className="text-sm font-semibold text-slate-700">{github_username}</p>
              <p className="text-sm text-slate-500">{user_email}</p>
            </>
          )}
        </div>
        <EditControls editing={editing} onEdit={open} onSave={() => { onChange(draft.github_username, draft.user_email); close(); }} onCancel={cancel} />
      </div>
    </SectionCard>
  );
}

// ─── Summary ──────────────────────────────────────────────────────────────────

function SummarySection({ summary, onChange }: { summary: string; onChange: (v: string) => void }) {
  const { editing, draft, setDraft, open, cancel, close } = useEditState(summary);
  return (
    <SectionCard title="Summary" icon="📝">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          {editing
            ? <Field value={draft} onChange={setDraft} multiline rows={4} />
            : <p className="text-sm text-slate-600 leading-relaxed">{summary}</p>
          }
        </div>
        <EditControls editing={editing} onEdit={open} onSave={() => { onChange(draft); close(); }} onCancel={cancel} />
      </div>
    </SectionCard>
  );
}

// ─── Education & Awards ───────────────────────────────────────────────────────
// TODO (backend): no backend source for this data — fully user-populated.
// EducationEntry is intentionally excluded from resumeTypes.ts.

interface EducationEntry { institution: string; degree: string; date_range: string; notes: string; }

const defaultEducation: EducationEntry[] = [{
  institution: "University of British Columbia Okanagan",
  degree: "Bachelor of Science, Computer Science",
  date_range: "Sep 2022 – Apr 2026",
  notes: "Dean's List 2023, 2024 · Relevant coursework: Algorithms, Databases, Software Engineering",
}];

function EducationSection() {
  const [entries, setEntries] = useState<EducationEntry[]>(defaultEducation);
  const [editingIdx, setEditingIdx] = useState<number | null>(null);
  const [draft, setDraft] = useState<EducationEntry | null>(null);

  const fields: { key: keyof EducationEntry; placeholder: string }[] = [
    { key: "institution", placeholder: "Institution" },
    { key: "degree",      placeholder: "Degree & Field of Study" },
    { key: "date_range",  placeholder: "Sep YYYY – Apr YYYY" },
    { key: "notes",       placeholder: "GPA, awards, honours…" },
  ];

  const save = () => {
    if (draft === null || editingIdx === null) return;
    setEntries(e => { const n = [...e]; n[editingIdx] = draft; return n; });
    setEditingIdx(null);
  };
  const add = () => {
    const blank = { institution: "Institution Name", degree: "Degree, Field of Study", date_range: "MMM YYYY – MMM YYYY", notes: "" };
    setEntries(e => [...e, blank]); setDraft(blank); setEditingIdx(entries.length);
  };

  return (
    <SectionCard title="Education & Awards" icon="🎓">
      <div className="space-y-4">
        {entries.map((entry, i) => (
          <div key={i}>
            {editingIdx === i && draft ? (
              <div className="space-y-2 p-3 rounded-xl bg-slate-50 border border-slate-200">
                {fields.map(({ key, placeholder }) => (
                  <Field key={key} value={draft[key]} onChange={v => setDraft(d => d ? { ...d, [key]: v } : d)} placeholder={placeholder} />
                ))}
                <EditControls editing onEdit={() => {}} onSave={save} onCancel={() => setEditingIdx(null)} />
              </div>
            ) : (
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                  <div className="flex items-baseline justify-between flex-wrap gap-2">
                    <span className="text-sm font-semibold text-slate-700">{entry.institution}</span>
                    <span className="text-xs text-slate-400">{entry.date_range}</span>
                  </div>
                  <p className="text-sm text-slate-600 mt-0.5">{entry.degree}</p>
                  {entry.notes && <p className="text-xs text-slate-400 mt-1 italic">{entry.notes}</p>}
                </div>
                <div className="flex gap-1.5 shrink-0">
                  <button onClick={() => { setDraft({ ...entry }); setEditingIdx(i); }} className="text-xs font-semibold text-indigo-500 border border-indigo-200 rounded-lg px-2.5 py-1 hover:bg-indigo-50 transition-all">Edit</button>
                  <button onClick={() => setEntries(e => e.filter((_, idx) => idx !== i))}  className="text-xs font-semibold text-red-400 border border-red-100 rounded-lg px-2.5 py-1 hover:bg-red-50 transition-all">✕</button>
                </div>
              </div>
            )}
          </div>
        ))}
        <button onClick={add} className="text-xs font-semibold text-indigo-500 border border-indigo-200 rounded-lg px-3 py-1.5 hover:bg-indigo-50 transition-all">+ Add Entry</button>
      </div>
    </SectionCard>
  );
}

// ─── Skills ───────────────────────────────────────────────────────────────────
// TODO (backend): aggregate skills across analyses; tiering needs future work

function SkillsSection({ skills, onChange }: { skills: string[]; onChange: (s: string[]) => void }) {
  const { editing, draft, setDraft, open, cancel, close } = useEditState(skills);
  return (
    <SectionCard title="Skills" icon="⚡">
      <div className="flex items-start justify-between gap-4 mb-3">
        <p className="text-xs text-slate-400">Detected from your repositories</p>
        <EditControls editing={editing} onEdit={open} onSave={() => { onChange(draft); close(); }} onCancel={cancel} />
      </div>
      <div className="flex flex-wrap gap-2">
        {(editing ? draft : skills).map(skill => (
          <Chip key={skill} label={skill} colorClass="bg-indigo-100 text-indigo-700"
            onRemove={editing ? () => setDraft(d => d.filter(s => s !== skill)) : undefined} />
        ))}
      </div>
      {editing && <AddChip placeholder="Add skill…" onAdd={v => { if (!draft.map(s => s.toLowerCase()).includes(v.toLowerCase())) setDraft(d => [...d, v]); }} />}
    </SectionCard>
  );
}

// ─── Projects ─────────────────────────────────────────────────────────────────
// collaboration_insight = user_role.blurb from infer_user_role() — serves as contribution evidence (prof requirement)
// TODO (milestone 3): decide what additional contribution fields to surface here

function ProjectEntry({ project, onSave }: { project: Project; onSave: (p: Project) => void }) {
  const { editing, draft, setDraft, open, cancel, close } = useEditState(project);
  const [fwInput, setFwInput] = useState("");
  const addFw = () => {
    const t = fwInput.trim();
    if (t && !draft.frameworks.includes(t)) setDraft(d => ({ ...d, frameworks: [...d.frameworks, t] }));
    setFwInput("");
  };
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 space-y-3">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1">
          {editing ? (
            <div className="flex gap-2 flex-wrap">
              <Field value={draft.name}       onChange={v => setDraft(d => ({ ...d, name: v }))}       placeholder="Project name" className="flex-1 font-semibold" />
              <Field value={draft.date_range} onChange={v => setDraft(d => ({ ...d, date_range: v }))} placeholder="Date range"   className="w-44" />
            </div>
          ) : (
            <div className="flex items-baseline justify-between flex-wrap gap-2">
              <span className="text-sm font-semibold text-slate-700">{project.name}</span>
              <span className="text-xs text-slate-400 shrink-0">{project.date_range}</span>
            </div>
          )}
        </div>
        <EditControls editing={editing} onEdit={open} onSave={() => { onSave(draft); close(); }} onCancel={cancel} />
      </div>
      <div>
        <div className="flex flex-wrap gap-2">
          {(editing ? draft.frameworks : project.frameworks).map(fw => (
            <Chip key={fw} label={fw} colorClass="bg-indigo-100 text-indigo-700"
              onRemove={editing ? () => setDraft(d => ({ ...d, frameworks: d.frameworks.filter(f => f !== fw) })) : undefined} />
          ))}
        </div>
        {editing && (
          <div className="flex gap-2 mt-2">
            <input value={fwInput} onChange={e => setFwInput(e.target.value)} onKeyDown={e => e.key === "Enter" && addFw()}
              placeholder="Add technology…" className={inputCls} />
            <button onClick={addFw} className="text-xs font-bold text-white bg-indigo-600 rounded-lg px-3 py-1 hover:bg-indigo-700 transition-all">+ Add</button>
          </div>
        )}
      </div>
      <div className="flex items-start gap-2 pt-1">
        <span className="text-indigo-500 text-xs font-bold mt-0.5 shrink-0">▸</span>
        {editing
          ? <Field value={draft.collaboration_insight} onChange={v => setDraft(d => ({ ...d, collaboration_insight: v }))} multiline rows={2} placeholder="Role description and contribution evidence…" />
          : <p className="text-sm text-slate-600 leading-relaxed">{project.collaboration_insight}</p>
        }
      </div>
    </div>
  );
}

function ProjectsSection({ projects, onChange }: { projects: Project[]; onChange: (p: Project[]) => void }) {
  const update = (i: number, p: Project) => { const next = [...projects]; next[i] = p; onChange(next); };
  return (
    <SectionCard title="Projects" icon="🗂️">
      <div className="space-y-3">
        {projects.map((p, i) => <ProjectEntry key={i} project={p} onSave={proj => update(i, proj)} />)}
      </div>
    </SectionCard>
  );
}

// ─── Programming Languages ────────────────────────────────────────────────────

function LanguagesSection({ languages, onChange }: { languages: Language[]; onChange: (l: Language[]) => void }) {
  const { editing, draft, setDraft, open, cancel, close } = useEditState(languages);
  const [input, setInput] = useState("");
  const add = () => {
    const t = input.trim();
    if (t && !draft.map(l => l.name.toLowerCase()).includes(t.toLowerCase())) setDraft(d => [...d, { name: t, file_count: 0 }]);
    setInput("");
  };
  const displayed = editing ? draft : languages;
  const maxFiles = Math.max(...displayed.map(l => l.file_count), 1);
  return (
    <SectionCard title="Programming Languages" icon="💻">
      <div className="flex items-center justify-between mb-3">
        <p className="text-xs text-slate-400">Bar width reflects file count from analysis</p>
        <EditControls editing={editing} onEdit={open} onSave={() => { onChange(draft); close(); }} onCancel={cancel} />
      </div>
      <div className="space-y-2.5">
        {displayed.map(lang => (
          <div key={lang.name} className="flex items-center gap-3">
            <span className="w-24 text-right text-xs font-bold text-slate-500 font-mono shrink-0">{lang.name}</span>
            <div className="flex-1 h-7 bg-slate-100 rounded-lg overflow-hidden relative">
              <div className="h-full rounded-lg bg-indigo-200" style={{ width: `${lang.file_count === 0 ? 4 : (lang.file_count / maxFiles) * 100}%`, opacity: lang.file_count === 0 ? 0.4 : 1 }} />
              <span className="absolute inset-0 flex items-center px-2.5 text-xs font-semibold text-indigo-800">
                {lang.file_count > 0 ? `${lang.file_count} file${lang.file_count !== 1 ? "s" : ""}` : "—"}
              </span>
            </div>
            {editing && <button onClick={() => setDraft(d => d.filter(l => l.name !== lang.name))} className="!bg-transparent !border-none text-red-300 hover:text-red-400 text-xl shrink-0">×</button>}
          </div>
        ))}
      </div>
      {editing && (
        <div className="flex gap-2 mt-3">
          <input value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === "Enter" && add()} placeholder="Add language…" className={inputCls} />
          <button onClick={add} className="text-xs font-bold text-white bg-indigo-600 rounded-lg px-3 py-1 hover:bg-indigo-700 transition-all">+ Add</button>
        </div>
      )}
    </SectionCard>
  );
}

// ─── Download placeholder ─────────────────────────────────────────────────────
// TODO (frontend): implement export using the `docx` npm package — no backend changes needed

function DownloadButton() {
  const [showTip, setShowTip] = useState(false);
  return (
    <div className="relative inline-block">
      <button disabled onMouseEnter={() => setShowTip(true)} onMouseLeave={() => setShowTip(false)}
        className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold border bg-white text-slate-400 border-slate-200 cursor-not-allowed opacity-60">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="7 10 12 15 17 10" /><line x1="12" y1="15" x2="12" y2="3" />
        </svg>
        Download Resume
        <span className="text-xs font-bold uppercase tracking-wider bg-slate-100 text-slate-400 rounded-full px-2 py-0.5">Soon</span>
      </button>
      {showTip && (
        <div className="absolute bottom-full right-0 mb-2 z-10 bg-white border border-slate-200 rounded-xl shadow-md px-3 py-2 text-xs text-slate-500 whitespace-nowrap">
          Export to .docx / .pdf — planned for a future sprint
        </div>
      )}
    </div>
  );
}

// ─── Main page ────────────────────────────────────────────────────────────────

export default function ResumeDisplay( {onPrevious, onComplete} : {onPrevious?: () => void, onComplete?: () => void}) {
  const [resume, setResume] = useState<Resume>(mockResume);
  return (
    <div className="min-h-screen bg-slate-50 font-sans">
      <div className="max-w-4xl mx-auto px-6 py-10">
        <div className="mb-6">
          <p className="text-xs font-semibold uppercase tracking-widest text-indigo-500 mb-1">Resume Display &amp; Editor</p>
          <div className="flex items-center justify-between flex-wrap gap-3">
            <h1 className="text-3xl font-bold text-slate-800">Your generated résumé.</h1>
            <DownloadButton />
          </div>
        </div>
        <div className="space-y-5">
          <ContactSection github_username={resume.github_username ?? ""} user_email={resume.user_email ?? ""} onChange={(u, e) => setResume(r => ({ ...r, github_username: u, user_email: e }))} />
          <SummarySection  summary={resume.summary}   onChange={s => setResume(r => ({ ...r, summary: s }))} />
          <EducationSection />
          <SkillsSection   skills={resume.skills}     onChange={s => setResume(r => ({ ...r, skills: s }))} />
          <ProjectsSection projects={resume.projects} onChange={p => setResume(r => ({ ...r, projects: p }))} />
          <LanguagesSection languages={resume.languages} onChange={l => setResume(r => ({ ...r, languages: l }))} />
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
        <p className="text-center text-xs text-slate-300 mt-8">Edits are session-only · Export available in a future release</p>
      </div>
    </div>
  );
}