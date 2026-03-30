import { useState, useEffect } from "react";
import { useNavigate, useParams } from 'react-router-dom';
import SectionCard from "../components/SectionCard";
import type { Resume, Project, Language, EducationEntry, WorkEntry, AwardEntry } from "../types/resumeTypes";
import ResumePreviewModal from "../components/resumePreviewModal";

export const LIMITS = {
  summary: { bullets: 3, chars:180 },
  work: { entries: 3, bullets: 3, chars: 180 },
  education: { entries: 3, chars: 180 },
  awards: { entries: 2, bullets: 2, chars: 180 },
  projects: { entries: 3, chars: 180},
  skills: {entries: 15},
} as const;

// ─── Mock data ────────────────────────────────────────────────────────────────

export const mockResume: Resume = {
  analysis_id: "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  full_name: "John Doe",
  github_username: "yourusername",
  user_email: "you@example.com",
  phone: "123-456-7890",
  linkedin: "linkedin.com/in/yourusername",
  summary: [
    "Full-stack developer with experience building collaborative web and mobile applications. Strong version control practices and a focus on clean, maintainable code.",
    "Passionate about learning new technologies and applying them to solve real-world problems. Seeking opportunities to contribute to impactful projects and grow as a software engineer.",
  ],
  projects: [
    {
      name: "Capstone Analysis Tool", date_range: "Jan 2025 - Apr 2025",
      collaboration: "Contributed a substantial amount of new code, indicating a strong role in implementing features and expanding the project's functionality.",
      frameworks: ["Python", "FastAPI", "PostgreSQL", "Docker", "Flask"],
    },
    {
      name: "COSC 360 – Android App", date_range: "Apr 2025 - Present",
      collaboration: "Most contributions involved modifying existing files, suggesting a maintenance-focused role aimed at improving correctness and performance.",
      frameworks: ["Java", "Android SDK", "XML", "SQLite"],
    },
    {
      name: "Personal Portfolio", date_range: "Feb 2025 - Mar 2025",
      collaboration: "Balanced contribution pattern across additions, modifications, and deletions throughout the codebase.",
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
  education: [
    { 
      institution: "University of British Columbia Okanagan",
      degree: "Bachelor of Science",
      major: "Computer Science",
      date_range: "Sep 2022 – Apr 2026",
      notes: "Dean's List 2023, 2024 · Relevant coursework: Algorithms, Databases, Software Engineering",
    },
  ],
  awards: [
    {
      title: "Test Scholars Award",
      issuer: "University of British Columbia Okanagan",
      date: "Apr 2024",
      description: [
        "Awarded to top 5% of students in each faculty based on academic performance and extracurricular involvement.",
        "Recognizes consistent excellence across all courses and contributions to the university community.",
      ],
    },
  ],
  work_experience: [
    {
      company: "UBC Okanagan Computer Science Department",
      role: "Undergraduate Teaching Assistant",
      date_range: "Sep 2023 – Apr 2024",
      location: "Kelowna, BC",
      description: [
        "Led weekly lab sessions for 30+ students in an introductory programming course, providing guidance on Java and Python assignments.",
        "Held regular office hours to assist students with debugging and understanding core programming concepts.",
      ],
    },
  ],
};

// ─── API ───────────────────────────────────────────────────────────────
const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8080";

async function fetchResume(resumeId: string, githubUsername: string, userEmail: string): Promise<Resume> {
  const res = await fetch(`${API_BASE}/resume/${resumeId}`);
  if (!res.ok) throw new Error(`Failed to fetch resume: ${res.status} ${res.statusText}`);
  const data = await res.json();
  console.log("Raw API response", data)
  const r = data.resume_data ?? data;
  console.log("parsed resume data", r)
  // Normalize fields to ensure they exist and have the expected structure
  return {
    analysis_id: r.analysis_id,
    summary: Array.isArray(r.summary) ? r.summary : [r.summary].filter(Boolean),
    education: Array.isArray(r.education) ? r.education : [],
    work_experience: Array.isArray(r.work_experience) ? r.work_experience : [],
    awards: Array.isArray(r.awards) ? r.awards : [],
    projects: (Array.isArray(r.projects) ? r.projects : []).slice(0, 3),
    skills: Array.isArray(r.skills) ? r.skills : [],
    languages: Array.isArray(r.languages) ? r.languages : [],
    full_name: r.full_name ?? "",
    github_username: r.github_username || githubUsername,
    user_email: r.user_email || userEmail,
    phone: r.phone ?? "",
    linkedin: r.linkedin ?? "",
  };
}

async function putResume(resumeId: string, resume: Resume): Promise<void> {
  const {resume_id, analysis_id, ...resumeData} = resume;
  const res = await fetch(`${API_BASE}/resume/${resumeId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resume_data: resumeData }),
  });
  if (!res.ok) throw new Error(`Failed to update resume: ${res.status} ${res.statusText}`);
}

// ─── Primitives ───────────────────────────────────────────────────────────────

const inputCls = "w-full border border-slate-200 rounded-lg px-3 py-1.5 text-sm text-slate-700 bg-slate-50 focus:outline-none focus:ring-2 focus:ring-indigo-300 transition-all";

// Display "current / max" entries
function EntryCount({current, max}: {current: number; max: number}){
  return (
    <span className={`text-xs font-semibold ${current==max? "text-red-400" : "text-slate-400"}`}>
      {current} / {max}
    </span>
  )
}

// Display "len/max" for character-limited fields
function CharCount({ value, max }: { value: string; max: number }) {
  const pct = value.length / max;
  const color = pct >= 1 ? "text-red-500" : pct >= 0.8 ? "text-amber-400" : "text-slate-300";
  return <span className={`text-[10px] tabular-nums text-right ${color}`}>{value.length}/{max}</span>;
}

function Field({ value, onChange, placeholder, multiline = false, rows = 3, className = "", maxChars }: {
  value: string; onChange: (v: string) => void; placeholder?: string;
  multiline?: boolean; rows?: number; className?: string; maxChars?: number;
}) {
  const props = { value, onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => onChange(e.target.value), placeholder, className: `${inputCls} ${className}` };
  return (
    <div className="w-full">
      {multiline
        ? <textarea {...props} rows={rows} className={`${props.className} resize-none`} />
        : <input    {...props} type="text" />}
      {maxChars !== undefined && <div className="flex justify-end mt-0.5"><CharCount value={value} max={maxChars} /></div>}
    </div>
  );
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

function AddChip({ placeholder, onAdd, disabled = false }: { placeholder: string; onAdd: (v: string) => void; disabled?: boolean }) {
  const [val, setVal] = useState("");
  const commit = () => { if (val.trim() && !disabled) { onAdd(val.trim()); setVal(""); } };
  return (
    <div className="flex gap-2 mt-2">
      <input value={val} onChange={e => setVal(e.target.value)} onKeyDown={e => e.key === "Enter" && commit()}
        placeholder={disabled ? "Limit reached" : placeholder} disabled={disabled} className={`${inputCls} disabled:opacity-50`} />
      <button onClick={commit} disabled={disabled} className="text-xs font-bold text-white bg-indigo-600 rounded-lg px-3 py-1 hover:bg-indigo-700 transition-all disabled:opacity-50">+ Add</button>
    </div>
  );
}

function AddNewButton({ label, onClick, disabled = false }: { label: string; onClick: () => void; disabled?: boolean }) {
  return (
    <button onClick={onClick} disabled={disabled}
      className="text-xs font-semibold text-indigo-500 border border-indigo-200 rounded-lg px-3 py-1 hover:bg-indigo-50 transition-all disabled:opacity-40 disabled:cursor-not-allowed">
      {label}
    </button>
  );
}

function EditControls({ editing, onEdit, onSave, onCancel, saving = false }: {
  editing: boolean; onEdit: () => void; onSave: () => void; onCancel: () => void; saving?: boolean;
}) {
  if (!editing) return (
    <button onClick={onEdit} className="text-xs font-semibold text-indigo-500 border border-indigo-200 rounded-lg px-3 py-1 hover:bg-indigo-50 transition-all">Edit</button>
  );
  return (
    <div className="flex gap-2">
      <button onClick={onSave} disabled = {saving}  className="text-xs font-bold text-white bg-indigo-600 rounded-lg px-3 py-1 hover:bg-indigo-700 transition-all disabled:opacity-50">{saving?"Saving...":"Save"}</button>
      <button onClick={onCancel} className="text-xs font-semibold text-slate-500 border border-slate-200 rounded-lg px-3 py-1 hover:bg-slate-50 transition-all">Cancel</button>
    </div>
  );
}

function useEditState<T>(value: T, initialEditing = false) {
  const [editing, setEditing] = useState(initialEditing);
  const [draft, setDraft] = useState<T>(value);
  const open   = () => { setDraft(value); setEditing(true); };
  const cancel = () => { setDraft(value); setEditing(false); };
  return { editing, draft, setDraft, open, cancel, close: () => setEditing(false) };
}

// Bullet list editor (used for Work Experience and Awards)
function BulletEditor({ bullets, onChange, maxBullets, maxChars }: { bullets: string[]; onChange: (b: string[]) => void; maxBullets: number; maxChars: number }) {
  const atLimit = bullets.length >= maxBullets;
  return (
    <div className="space-y-2 mt-2">
      {bullets.map((b, i) => (
        <div key={i} className="flex gap-2 items-start">
          <span className="text-indigo-400 text-xs font-bold mt-2 shrink-0">▸</span>
          <Field value={b} onChange={v => { const n = [...bullets]; n[i] = v; onChange(n); }} multiline rows={2} maxChars={maxChars} />
          <button onClick={() => onChange(bullets.filter((_, idx) => idx !== i))}
            className="!bg-transparent !border-none text-red-300 hover:text-red-400 text-xl mt-1 shrink-0">×</button>
        </div>
      ))}
      <div className="flex items-center gap-3">
        <button onClick={() => !atLimit && onChange([...bullets, ""])} disabled={atLimit}
          className="text-xs font-semibold text-indigo-500 border border-indigo-200 rounded-lg px-3 py-1 hover:bg-indigo-50 transition-all disabled:opacity-40 disabled:cursor-not-allowed">
          + Add bullet
        </button>
        <EntryCount current={bullets.length} max={maxBullets} />
      </div>
    </div>
  );
}
// ─── Contact ──────────────────────────────────────────────────────────────────

function ContactSection({ full_name, github_username, user_email, phone, linkedin, onChange }: {
  full_name: string; github_username: string; user_email: string; phone: string; linkedin: string; onChange: (fn: string, u: string, e: string, p: string, l: string) => void;
}) {
  const { editing, draft, setDraft, open, cancel, close } = useEditState({ full_name, github_username, user_email, phone, linkedin });
  return (
    <SectionCard title="Contact" icon="👤">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 space-y-2">
          {editing ? (
            <>
              <Field value={draft.full_name}       onChange={v => setDraft(d => ({ ...d, full_name: v }))} placeholder="Full Name" />
              <Field value={draft.github_username} onChange={v => setDraft(d => ({ ...d, github_username: v }))} placeholder="GitHub username" />
              <Field value={draft.user_email}      onChange={v => setDraft(d => ({ ...d, user_email: v }))}      placeholder="Email address" />
              <Field value={draft.phone}           onChange={v => setDraft(d => ({ ...d, phone: v }))}           placeholder="Phone number" />
              <Field value={draft.linkedin}        onChange={v => setDraft(d => ({ ...d, linkedin: v }))}        placeholder="LinkedIn profile" />
            </>
          ) : (
            <>
              <p className="text-sm font-semibold text-slate-700">{full_name}</p>
              {github_username && <p className="text-sm text-slate-500">github.com/{github_username}</p>}
              <p className="text-sm text-slate-500">{user_email}</p>
              <p className="text-sm text-slate-500">{phone}</p>
              <p className="text-sm text-slate-500">{linkedin}</p>
            </>
          )}
        </div>
        <EditControls editing={editing} onEdit={open} onSave={() => { onChange(draft.full_name, draft.github_username, draft.user_email, draft.phone, draft.linkedin); close(); }} onCancel={cancel} />
      </div>
    </SectionCard>
  );
}

// ─── Summary ──────────────────────────────────────────────────────────────────

function SummarySection({ summary, onChange }: { summary: string[]; onChange: (v: string[]) => void }) {
  const { editing, draft, setDraft, open, cancel, close } = useEditState(summary);
  return (
    <SectionCard title="Summary" icon="📝">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          {editing
            ? <BulletEditor bullets={draft} onChange={setDraft} maxBullets={LIMITS.summary.bullets} maxChars={LIMITS.summary.chars} />
            : <ul className="space-y-1">
                {summary.map((s, i) => (
                  <li key={i} className="flex items-start gap-2">
                  <span className="text-indigo-400 text-xs font-bold mt-0.5 shrink-0">▸</span>
                  <span className="text-sm text-slate-600 leading-relaxed">{s}</span>
                </li>
              ))}
            </ul>
          }
        </div>
        <EditControls editing={editing} onEdit={open} onSave={() => { onChange(draft); close(); }} onCancel={cancel} />
      </div>
    </SectionCard>
  );
}

// ─── Work Experience ───────────────────────────────────────────────────────

function WorkEntryCard({ entry, onSave, onDelete, autoEdit = false, onCancelNew }: {
  entry: WorkEntry; onSave: (e: WorkEntry) => void; onDelete: () => void; autoEdit?: boolean; onCancelNew?: () => void;
}) {
  const { editing, draft, setDraft, open, cancel, close } = useEditState(entry, autoEdit);
  const handleCancel = onCancelNew ?? cancel;
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 space-y-3">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1">
          {editing ? (
            <div className="space-y-2">
              <div className="flex gap-2 flex-wrap">
                <Field value={draft.company} onChange={v => setDraft(d => ({ ...d, company: v }))} placeholder="Company" className="flex-1 font-semibold" />
                <Field value={draft.role}    onChange={v => setDraft(d => ({ ...d, role: v }))}    placeholder="Role"    className="flex-1" />
              </div>
              <div className="flex gap-2 flex-wrap">
                <Field value={draft.date_range}     onChange={v => setDraft(d => ({ ...d, date_range: v }))}  placeholder="May YYYY – Aug YYYY"    className="flex-1" />
                <Field value={draft.location ?? ""} onChange={v => setDraft(d => ({ ...d, location: v }))}    placeholder="Location (optional)"    className="flex-1" />
              </div>
            </div>
          ) : (
            <div>
              <div className="flex items-baseline justify-between flex-wrap gap-2">
                <span className="text-sm font-semibold text-slate-700">{entry.company}</span>
                <span className="text-xs text-slate-400">{entry.date_range}</span>
              </div>
              <p className="text-sm text-slate-500">{entry.role}{entry.location ? ` · ${entry.location}` : ""}</p>
            </div>
          )}
        </div>
        <div className="flex gap-1.5 shrink-0">
          <EditControls editing={editing} onEdit={open} onSave={() => { onSave(draft); close(); }} onCancel={handleCancel} />
          {!editing && (
            <button onClick={onDelete} className="text-xs font-semibold text-red-400 border border-red-100 rounded-lg px-2.5 py-1 hover:bg-red-50 transition-all">✕</button>
          )}
        </div>
      </div>
      {editing
        ? <BulletEditor bullets={draft.description} onChange={v => setDraft(d => ({ ...d, description: v }))} maxBullets={LIMITS.work.bullets} maxChars={LIMITS.work.chars} />
        : <ul className="space-y-1">
            {entry.description.map((b, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="text-indigo-400 text-xs font-bold mt-0.5 shrink-0">▸</span>
                <span className="text-sm text-slate-600 leading-relaxed">{b}</span>
              </li>
            ))}
          </ul>
      }
    </div>
  );
}

function WorkExperienceSection({ work, onChange }: { work: WorkEntry[]; onChange: (w: WorkEntry[]) => void }) {
  const [newIdx, setNewIdx] = useState<number | null>(null);
  const blank: WorkEntry = { company: "", role: "", date_range: "", location: "", description: [""] };
  const atLimit = work.length >= LIMITS.work.entries;
  const addNew = () => {
    if (atLimit) return;
    setNewIdx(work.length);
    onChange([...work, blank]);
  };
  return (
    <SectionCard title="Work Experience" icon="💼">
      <div className="space-y-3">
        {work.map((entry, i) => (
          <WorkEntryCard key={i} entry={entry} autoEdit={i === newIdx}
            onSave={e  => { setNewIdx(null); const n = [...work]; n[i] = e; onChange(n); }}
            onDelete={() => { setNewIdx(null); onChange(work.filter((_, idx) => idx !== i))}}
            onCancelNew={i === newIdx ? () => { setNewIdx(null); onChange(work.filter((_, idx) => idx !== i))} : undefined}
          />
        ))}
        <div className="flex items-center gap-3">
          <AddNewButton label="+ Add Position" onClick={addNew} disabled={atLimit} />
          <EntryCount current={work.length} max={LIMITS.work.entries} />
        </div>
      </div>
    </SectionCard>
  );
}

// ─── Education ───────────────────────────────────────────────────────
// no backend source for this data — fully user-populated.

function EducationSection({ education, onChange }: { education: EducationEntry[]; onChange: (e: EducationEntry[]) => void }) {
  const [editingIdx, setEditingIdx] = useState<number | null>(null);
  const [draft, setDraft] = useState<EducationEntry | null>(null);
  const blank: EducationEntry = { institution: "", degree: "", major: "", minor: "", date_range: "", notes: "" };
  const atLimit = education.length >= LIMITS.education.entries;

  const save = () => {
    if (draft === null || editingIdx === null) return;
    const next = [...education]; next[editingIdx] = draft; onChange(next); setEditingIdx(null); setDraft(null);
  };
  const add = () => {
    if (atLimit) return;
    onChange([...education, { ...blank}]);
    setDraft({ ...blank });
    setEditingIdx(education.length);
  };

  return (
    <SectionCard title="Education" icon="🎓">
      <div className="space-y-4">
        {education.map((entry, i) => (
          <div key={i}>
            {editingIdx === i && draft ? (
              <div className="space-y-2 p-3 rounded-xl bg-slate-50 border border-slate-200">
                <Field value={draft.institution} onChange={v => setDraft(d => d && ({ ...d, institution: v }))} placeholder="Institution" />
                <div className="flex gap-2">
                  <Field value={draft.degree}    onChange={v => setDraft(d => d && ({ ...d, degree: v }))}     placeholder="Degree (e.g. Bachelor of Science)" className="flex-1" />
                  <Field value={draft.date_range} onChange={v => setDraft(d => d && ({ ...d, date_range: v }))} placeholder="Date Range: ex:Sep 2020 – May 2024"              className="flex-1" />
                </div>
                <div className="flex gap-2">
                  <Field value={draft.major ?? ""} onChange={v => setDraft(d => d && ({ ...d, major: v }))} placeholder="Major (optional)" className="flex-1" />
                  <Field value={draft.minor ?? ""} onChange={v => setDraft(d => d && ({ ...d, minor: v }))} placeholder="Minor (optional)" className="flex-1" />
                </div>
                <Field value={draft.notes} onChange={v => setDraft(d => d && ({ ...d, notes: v }))} placeholder="Other Notes: (e.g. GPA, honours, relevant coursework…)" maxChars={LIMITS.education.chars} />
                <EditControls editing onEdit={() => {}} onSave={save} onCancel={() => { setEditingIdx(null); setDraft(null); }} />
              </div>
            ) : (
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                  <div className="flex items-baseline justify-between flex-wrap gap-2">
                    <span className="text-sm font-semibold text-slate-700">{entry.institution}</span>
                    <span className="text-xs text-slate-400">{entry.date_range}</span>
                  </div>
                  <p className="text-sm text-slate-600 mt-0.5">{entry.degree} {entry.major ? `Major in ${entry.major}` : ""} {entry.minor ? ` · Minor in ${entry.minor}` : ""}</p>
                  {entry.notes && <p className="text-xs text-slate-400 mt-1 italic">{entry.notes}</p>}
                </div>
                <div className="flex gap-1.5 shrink-0">
                  <button onClick={() => { setDraft({ ...entry }); setEditingIdx(i); }} className="text-xs font-semibold text-indigo-500 border border-indigo-200 rounded-lg px-2.5 py-1 hover:bg-indigo-50 transition-all">Edit</button>
                  <button onClick={() => onChange(education.filter((_, idx) => idx !== i))}  className="text-xs font-semibold text-red-400 border border-red-100 rounded-lg px-2.5 py-1 hover:bg-red-50 transition-all">✕</button>
                </div>
              </div>
            )}
          </div>
        ))}
        <div className="flex items-center gap-3">
          <button onClick={add} disabled={atLimit} className="text-xs font-semibold text-indigo-500 border border-indigo-200 rounded-lg px-3 py-1.5 hover:bg-indigo-50 transition-all disabled:opacity-40 disabled:cursor-not-allowed">+ Add Entry</button>
          <EntryCount current={education.length} max={LIMITS.education.entries} />
        </div>
      </div>
    </SectionCard>
  );
}

// ─── Awards ───────────────────────────────────────────────────────────────────
function AwardEntryCard({ entry, onSave, onDelete, autoEdit = false, onCancelNew }: {
  entry: AwardEntry; onSave: (e: AwardEntry) => void; onDelete: () => void;
  autoEdit?: boolean; onCancelNew?: () => void;
}) {
  const { editing, draft, setDraft, open, cancel, close } = useEditState(entry, autoEdit);
  const handleCancel = onCancelNew ?? cancel;
 
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 space-y-3">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1">
          {editing ? (
            <div className="flex gap-2 flex-wrap">
              <Field value={draft.title}  onChange={v => setDraft(d => ({ ...d, title: v }))}  placeholder="Award title"  className="flex-1 font-semibold" />
              <Field value={draft.issuer} onChange={v => setDraft(d => ({ ...d, issuer: v }))} placeholder="Issuer"       className="flex-1" />
              <Field value={draft.date}   onChange={v => setDraft(d => ({ ...d, date: v }))}   placeholder="Year or date" className="w-32" />
            </div>
          ) : (
            <div className="flex items-baseline justify-between flex-wrap gap-2">
              <span className="text-sm font-semibold text-slate-700">{entry.title}</span>
              <span className="text-xs text-slate-400">{entry.issuer} · {entry.date}</span>
            </div>
          )}
        </div>
        <div className="flex gap-1.5 shrink-0">
          <EditControls editing={editing} onEdit={open} onSave={() => { onSave(draft); close(); }} onCancel={handleCancel} />
          {!editing && (
            <button onClick={onDelete} className="text-xs font-semibold text-red-400 border border-red-100 rounded-lg px-2.5 py-1 hover:bg-red-50 transition-all">✕</button>
          )}
        </div>
      </div>
      {editing
        ? <BulletEditor bullets={draft.description} onChange={v => setDraft(d => ({ ...d, description: v }))} maxBullets={LIMITS.awards.bullets} maxChars={LIMITS.awards.chars} />
        : <ul className="space-y-1">
            {entry.description.map((b, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="text-indigo-400 text-xs font-bold mt-0.5 shrink-0">▸</span>
                <span className="text-sm text-slate-600 leading-relaxed">{b}</span>
              </li>
            ))}
          </ul>
      }
    </div>
  );
}
 
function AwardsSection({ awards, onChange }: { awards: AwardEntry[]; onChange: (a: AwardEntry[]) => void }) {
  const [newIdx, setNewIdx] = useState<number | null>(null);
  const blank: AwardEntry = { title: "", issuer: "", date: "", description: [""] };
  const atLimit = awards.length >= LIMITS.awards.entries;
  const addNew = () => {if(atLimit) return; setNewIdx(awards.length); onChange([...awards, { ...blank }]); };
 
  return (
    <SectionCard title="Awards & Honours" icon="🏆">
      <div className="space-y-3">
        {awards.map((entry, i) => (
          <AwardEntryCard key={i} entry={entry}
            autoEdit={i === newIdx}
            onSave={e  => { setNewIdx(null); const n = [...awards]; n[i] = e; onChange(n); }}
            onDelete={() => { setNewIdx(null); onChange(awards.filter((_, idx) => idx !== i)); }}
            onCancelNew={i === newIdx ? () => { setNewIdx(null); onChange(awards.filter((_, idx) => idx !== i)); } : undefined}
          />
        ))}
        <div className="flex items-center gap-3">
          <AddNewButton label="+ Add Award" onClick={addNew} disabled={atLimit} />
          <EntryCount current={awards.length} max={LIMITS.awards.entries} />
        </div>
      </div>
    </SectionCard>
  );
}
// ─── Skills ───────────────────────────────────────────────────────────────────
// TODO (backend): aggregate skills across analyses; tiering needs future work

function SkillsSection({ skills, onChange }: { skills: string[]; onChange: (s: string[]) => void }) {
  const { editing, draft, setDraft, open, cancel, close } = useEditState(skills);
  const atLimit = draft.length >= LIMITS.skills.entries;
  return (
    <SectionCard title="Skills" icon="⚡">
      <div className="flex items-start justify-between gap-4 mb-3">
        <p className="text-xs text-slate-400">Detected from your repositories</p>
        <div className="flex items-center gap-2">
          {editing && <EntryCount current={draft.length} max={LIMITS.skills.entries} />}
          <EditControls editing={editing} onEdit={open} onSave={() => { onChange(draft); close(); }} onCancel={cancel} />
        </div>
      </div>
      <div className="flex flex-wrap gap-2">
        {(editing ? draft : skills).map(skill => (
          <Chip key={skill} label={skill} colorClass="bg-indigo-100 text-indigo-700"
            onRemove={editing ? () => setDraft(d => d.filter(s => s !== skill)) : undefined} />
        ))}
      </div>
      {editing && <AddChip placeholder="Add skill…" disabled={atLimit} onAdd={v => { if (!draft.map(s => s.toLowerCase()).includes(v.toLowerCase())) setDraft(d => [...d, v]); }} />}
    </SectionCard>
  );
}

// ─── Projects ─────────────────────────────────────────────────────────────────

function ProjectEntry({ project, onSave, onDelete, autoEdit = false, onCancelNew }: {
  project: Project; onSave: (p: Project) => void; onDelete: () => void; autoEdit?: boolean; onCancelNew?: () => void;
}) {
  const { editing, draft, setDraft, open, cancel, close } = useEditState(project, autoEdit);
  const handleCancel = onCancelNew ?? cancel;
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
        <div className="flex gap-1.5 shrink-0">
          <EditControls editing={editing} onEdit={open} onSave={() => { onSave(draft); close(); }} onCancel={handleCancel} />
          {!editing && (
            <button onClick={onDelete} className="text-xs font-semibold text-red-400 border border-red-100 rounded-lg px-2.5 py-1 hover:bg-red-50 transition-all">✕</button>
          )}
        </div>
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
          ? <Field value={draft.collaboration} onChange={v => setDraft(d => ({ ...d, collaboration: v }))} multiline rows={2} placeholder="Role description and contribution evidence…" maxChars={LIMITS.projects.chars} />
          : <p className="text-sm text-slate-600 leading-relaxed">{project.collaboration}</p>
        }
      </div>
    </div>
  );
}

function ProjectsSection({ projects, onChange }: { projects: Project[]; onChange: (p: Project[]) => void }) {
  const [newIdx, setNewIdx] = useState<number | null>(null);
  const blank: Project = { name: "", date_range: "", collaboration: "", frameworks: [] };
  const atLimit = projects.length >= LIMITS.projects.entries;
  const addNew = () => {
    if (atLimit) return;
    setNewIdx(projects.length);
    onChange([...projects, { ...blank }]);
  };
  const update = (i: number, p: Project) => { const next = [...projects]; next[i] = p; onChange(next); };
  return (
    <SectionCard title="Projects" icon="🗂️">
      <div className="space-y-3">
        {projects.map((p, i) => (
          <ProjectEntry key={i} project={p} autoEdit={i === newIdx}
            onSave={proj => { setNewIdx(null); update(i, proj); }}
            onDelete={() => { setNewIdx(null); onChange(projects.filter((_, idx) => idx !== i)); }}
            onCancelNew={i === newIdx ? () => { setNewIdx(null); onChange(projects.filter((_, idx) => idx !== i)); } : undefined}
          />
        ))}
        <div className="flex items-center gap-3">
          <AddNewButton label="+ Add Project" onClick={addNew} disabled={atLimit} />
          <EntryCount current={projects.length} max={LIMITS.projects.entries} />
        </div>
      </div>
    </SectionCard>
  );
}

// ─── Programming Languages ────────────────────────────────────────────────────

// ─── Programming Languages ────────────────────────────────────────────────────
 
function LanguagesSection({ languages, onChange }: { languages: Language[]; onChange: (l: Language[]) => void }) {
  const { editing, draft, setDraft, open, cancel, close } = useEditState(languages);
  const [langInput, setLangInput] = useState("");
  const [fileInput, setFileInput] = useState("");
  const addLang = () => {
    const t = langInput.trim();
    if (t && !draft.map(l => l.name.toLowerCase()).includes(t.toLowerCase())) {
      setDraft(d => [...d, { name: t, file_count: Math.max(0, parseInt(fileInput) || 0) }]);
    }
    setLangInput(""); setFileInput("");
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
            {editing && (
              <div className="flex items-center gap-1.5 shrink-0">
                <input
                  type="number" min="0"
                  value={lang.file_count}
                  onChange={e => setDraft(d => d.map(l => l.name === lang.name ? { ...l, file_count: Math.max(0, parseInt(e.target.value) || 0) } : l))}
                  className="w-16 border border-slate-200 rounded-lg px-2 py-1 text-xs text-slate-700 bg-slate-50 focus:outline-none focus:ring-2 focus:ring-indigo-300 text-center"
                />
                <button onClick={() => setDraft(d => d.filter(l => l.name !== lang.name))} className="!bg-transparent !border-none text-red-300 hover:text-red-400 text-xl shrink-0">×</button>
              </div>
            )}
          </div>
        ))}
      </div>
      {editing && (
        <div className="flex gap-2 mt-3">
          <input value={langInput} onChange={e => setLangInput(e.target.value)} onKeyDown={e => e.key === "Enter" && addLang()}
            placeholder="Add language…" className={inputCls} />
          <input type="number" min="0" value={fileInput} onChange={e => setFileInput(e.target.value)} onKeyDown={e => e.key === "Enter" && addLang()}
            placeholder="Files" className="w-20 border border-slate-200 rounded-lg px-3 py-1.5 text-sm text-slate-700 bg-slate-50 focus:outline-none focus:ring-2 focus:ring-indigo-300 text-center" />
          <button onClick={addLang} className="text-xs font-bold text-white bg-indigo-600 rounded-lg px-3 py-1 hover:bg-indigo-700 transition-all">+ Add</button>
        </div>
      )}
    </SectionCard>
  );
}

// ─── Preview/Download placeholder ─────────────────────────────────────────────────────
function PreviewButton({ resume }: { resume: Resume }) {
  const [open, setOpen] = useState(false);
  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold bg-[#6378ff] text-white hover:bg-indigo-700 transition-all shadow-sm"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="7 10 12 15 17 10" /><line x1="12" y1="15" x2="12" y2="3" />
        </svg>
        Download Resume
      </button>
      {open && <ResumePreviewModal resume={resume} onClose={() => setOpen(false)} />}
    </>
  );
}

// ─── Main page ────────────────────────────────────────────────────────────────

export default function ResumeDisplay({
  onPrevious,
  onComplete,
  resumeId: resumeIdProp,
  githubUsername = "",
  userEmail = "",
  viewMode = 'pipeline',
}: {
  onPrevious?: () => void;
  onComplete?: () => void;
  resumeId?: number | null;
  githubUsername?: string;
  userEmail?: string;
  viewMode?: 'pipeline' | 'standalone';
}) {
  const navigate = useNavigate();
  const params = useParams();
  const routeResumeId = params.id ? parseInt(params.id, 10) : null;
  const parsedId = resumeIdProp ?? (Number.isNaN(routeResumeId) ? null : routeResumeId);

  const [resume, setResume] = useState<Resume>({...mockResume, github_username: githubUsername || mockResume.github_username, user_email: userEmail || mockResume.user_email});
  const [loading, setLoading] = useState(parsedId !== null);
    const [error,   setError]   = useState<string | null>(null);
    const [saving,  setSaving]  = useState(false);
  
    useEffect(() => {
      if (parsedId === null) return;
      fetchResume(parsedId.toString(), githubUsername, userEmail)
        .then(r  => { setResume(r); setLoading(false); })
        .catch(e => { setError(e.message); setLoading(false); });
    }, [parsedId, githubUsername, userEmail]);
  
    // Merges a partial update into state and immediately PUTs to the backend.
    // In mock mode (no parsedId) the PUT is skipped — changes are session-only.
    const update = async (patch: Partial<Resume>) => {
      const next = { ...resume, ...patch };
      setResume(next);
      if (parsedId === null) return;
      setSaving(true);
      try   { await putResume(parsedId.toString(), next); }
      catch (e) { setError(e instanceof Error ? e.message : "Save failed"); }
      finally   { setSaving(false); }
    };
  
    if (loading) return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <p className="text-sm text-slate-400">Loading resume…</p>
      </div>
    );
  
  return (
    <div className="min-h-screen bg-slate-50 font-sans">
      <div className="max-w-4xl mx-auto px-6 py-10">
        <div className="mb-6">
          <p className="text-xs font-semibold uppercase tracking-widest text-indigo-500 mb-1">Resume Display &amp; Editor</p>
          <div className="flex items-center justify-between flex-wrap gap-3">
            <h1 className="text-3xl font-bold text-slate-800">Your generated resume.</h1>
            <PreviewButton resume={resume} />
          </div>
          {saving && <p className="text-xs text-indigo-400 mt-1">Saving…</p>}
          {error  && <p className="text-xs text-red-400   mt-1">Error: {error}</p>}
        </div>
        <div className="space-y-5">
          <ContactSection full_name={resume.full_name ?? ""} github_username={resume.github_username ?? ""} user_email={resume.user_email ?? ""} phone={resume.phone ?? ""} linkedin={resume.linkedin ?? ""} onChange={(fn, u, e, p, l) => update({full_name: fn, github_username: u, user_email: e, phone: p, linkedin: l })} />
          <SummarySection  summary={resume.summary} onChange={s => update({summary: s })} />
          <WorkExperienceSection
            work={resume.work_experience}
            onChange={w => update({ work_experience: w })} />
          <EducationSection
            education={resume.education}
            onChange={e => update({ education: e })} />
          <AwardsSection
            awards={resume.awards}
            onChange={a => update({ awards: a })} />
          <SkillsSection   skills={resume.skills}     onChange={s => update({skills: s })} />
          <ProjectsSection projects={resume.projects} onChange={p => update({ projects: p })} />
          <LanguagesSection languages={resume.languages} onChange={l => update({languages: l })} />
          </div>
          <div className="flex justify-between mt-8">
            {viewMode === 'pipeline' ? (
              <>
                <button
                  onClick={() => (onPrevious ? onPrevious() : navigate('/analysis/new/insights'))}
                  className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-bold text-white bg-indigo-400 shadow-sm hover:bg-indigo-700 transition-all"
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M19 12H5M12 19l-7-7 7-7" />
                  </svg>
                  Back
                </button>

                <button
                  onClick={() => (onComplete ? onComplete() : navigate('/analysis/new/portfolio'))}
                  className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-bold text-white bg-indigo-400 shadow-sm hover:bg-indigo-700 transition-all"
                >
                  Next
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M5 12h14M12 5l7 7-7 7" />
                  </svg>
                </button>
              </>
            ) : (
              <button
                onClick={() => navigate('/dashboard')}
                className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-bold text-white bg-indigo-400 shadow-sm hover:bg-indigo-700 transition-all"
              >
                Return to Dashboard
              </button>
            )}
          </div>
        <p className="text-center text-xs text-slate-300 mt-8">{parsedId ? "Changes save automatically" : "Edits are session-only · connect a resume ID to persist"}</p>
      </div>
    </div>
  );
}