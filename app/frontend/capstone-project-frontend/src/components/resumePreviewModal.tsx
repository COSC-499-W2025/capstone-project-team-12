import { useRef, useState } from "react";
import type { Resume } from "../types/resumeTypes";
import { downloadDocx, downloadPdf } from "../utils/resumeExports";

// ─── Preview primitives ───────────────────────────────────────────────────────

function SectionHead({ title }: { title: string }) {
  return (
    <div className="mt-3 mb-1">
      <p className="text-[10px] font-bold tracking-[0.1em] uppercase text-[#0f1629]">{title}</p>
      <div className="border-b border-[#0f1629] mb-1" />
    </div>
  );
}

function TwoCol({ left, right, leftBold = false }: { left: string; right: string; leftBold?: boolean }) {
  return (
    <div className="flex justify-between items-baseline gap-2 mb-0.5">
      <span className={`text-[11px] text-[#0f1629] ${leftBold ? "font-bold" : "font-normal"}`}>{left}</span>
      <span className="text-[10px] text-[#6b7280] shrink-0">{right}</span>
    </div>
  );
}

function Bullet({ text }: { text: string }) {
  return (
    <div className="flex gap-1.5 mb-0.5">
      <span className="text-[11px] text-[#0f1629] shrink-0 mt-px">•</span>
      <span className="text-[11px] text-[#0f1629] leading-snug">{text}</span>
    </div>
  );
}

function Sub({ text, italic = false }: { text: string; italic?: boolean }) {
  return (
    <p className={`text-[11px] text-[#64748b] mb-0.5 ${italic ? "italic" : ""}`}>{text}</p>
  );
}

// ─── Section components ───────────────────────────────────────────────────────

function PreviewContact({ r }: { r: Resume }) {
  const parts = [
    r.user_email,
    r.github_username && `github.com/${r.github_username}`,
    r.phone,
    r.linkedin,
  ].filter(Boolean);

  return (
    <div className="text-center mb-3">
      <p className="text-[18px] font-bold tracking-tight text-[#0f1629] mb-0.5">
        {r.full_name || r.github_username || "Resume"}
      </p>
      <p className="text-[10px] text-[#6b7280]">{parts.join("  |  ")}</p>
    </div>
  );
}

function PreviewSummary({ summary }: { summary: string[] }) {
  if (!summary.length) return null;
  return (
    <>
      <SectionHead title="Summary" />
      {summary.map((s, i) => <Bullet key={i} text={s} />)}
      <div className="mb-2" />
    </>
  );
}

function PreviewWork({ work }: { work: Resume["work_experience"] }) {
  if (!work.length) return null;
  return (
    <>
      <SectionHead title="Work Experience" />
      {work.map((w, i) => (
        <div key={i} className="mb-2">
          <TwoCol left={`${w.role} — ${w.company}`} right={w.date_range} leftBold />
          {w.location && <Sub text={w.location} italic />}
          {w.description.map((d, j) => <Bullet key={j} text={d} />)}
        </div>
      ))}
    </>
  );
}

function PreviewEducation({ education }: { education: Resume["education"] }) {
  if (!education.length) return null;
  return (
    <>
      <SectionHead title="Education" />
      {education.map((e, i) => (
        <div key={i} className="mb-2">
          <TwoCol left={e.institution} right={e.date_range} leftBold />
          <Sub text={[e.degree, e.major && `Major in ${e.major}`, e.minor && `Minor in ${e.minor}`].filter(Boolean).join(" · ")} />
          {e.notes && <Sub text={e.notes} italic />}
        </div>
      ))}
    </>
  );
}

function PreviewProjects({ projects }: { projects: Resume["projects"] }) {
  if (!projects.length) return null;
  return (
    <>
      <SectionHead title="Projects" />
      {projects.map((p, i) => (
        <div key={i} className="mb-2">
          <TwoCol left={p.name} right={p.date_range} leftBold />
          {p.frameworks.length > 0 && <Sub text={`Technologies: ${p.frameworks.join(", ")}`} />}
          <Bullet text={p.collaboration} />
        </div>
      ))}
    </>
  );
}

function PreviewAwards({ awards }: { awards: Resume["awards"] }) {
  if (!awards.length) return null;
  return (
    <>
      <SectionHead title="Awards & Honours" />
      {awards.map((a, i) => (
        <div key={i} className="mb-2">
          <TwoCol left={`${a.title} — ${a.issuer}`} right={a.date} leftBold />
          {a.description.map((d, j) => <Bullet key={j} text={d} />)}
        </div>
      ))}
    </>
  );
}

function PreviewSkills({ skills }: { skills: string[] }) {
  if (!skills.length) return null;
  return (
    <>
      <SectionHead title="Skills" />
      <p className="text-[11px] text-[#0f1629] mb-2">{skills.join("  ·  ")}</p>
    </>
  );
}

function PreviewLanguages({ languages }: { languages: Resume["languages"] }) {
  if (!languages.length) return null;
  return (
    <>
      <SectionHead title="Programming Languages" />
      <p className="text-[11px] text-[#0f1629] mb-2">{languages.map(l => l.name).join("  ·  ")}</p>
    </>
  );
}

// ─── Modal ────────────────────────────────────────────────────────────────────

export default function ResumePreviewModal({ resume, onClose }: { resume: Resume; onClose: () => void }) {
  const previewRef = useRef<HTMLDivElement>(null);
  const [busy, setBusy] = useState<"docx" | "pdf" | null>(null);

  const handleDocx = async () => {
    setBusy("docx");
    try   { await downloadDocx(resume); }
    catch (e) {console.error("Failed to download DOCX:", e); alert("Sorry, something went wrong while generating the DOCX file.");}
    finally { setBusy(null); }
  };

  const handlePdf = () => {
    if (!previewRef.current) return;
    setBusy("pdf");
    downloadPdf(previewRef.current);
    setBusy(null);
  };

  return (
    <div onClick={onClose} className="fixed inset-0 z-50 flex items-start justify-center bg-black/50 overflow-y-auto py-10">
      <div onClick={e => e.stopPropagation()} className="flex flex-col items-center gap-4 w-max">

        {/* Toolbar */}
        <div className="flex items-center justify-between gap-3 w-full bg-white rounded-xl shadow-md px-5 py-3">
          <p className="text-[11px] font-bold tracking-[0.1em] uppercase text-[#6b7280]">Resume Preview</p>
          <div className="flex items-center gap-2">
            <button onClick={handleDocx} disabled={busy !== null}
              className="text-xs font-bold text-white bg-[#6378ff] rounded-lg px-4 py-1.5 hover:bg-indigo-700 transition-all disabled:opacity-50">
              {busy === "docx" ? "Generating…" : "Download DOCX"}
            </button>
            <button onClick={handlePdf} disabled={busy !== null}
              className="text-xs font-bold text-white bg-[#0f1629] rounded-lg px-4 py-1.5 hover:bg-slate-800 transition-all disabled:opacity-50">
              {busy === "pdf" ? "Generating…" : "Download PDF"}
            </button>
            <button onClick={onClose}
              className="text-xs font-semibold text-[#64748b] border border-[#eef0f6] rounded-lg px-3 py-1.5 hover:bg-[#eef0f6] transition-all">
              Close
            </button>
          </div>
        </div>

        {/* Paper */}
        <div ref={previewRef} className="shadow-2xl rounded-sm bg-white w-[816px] min-h-[1056px] px-12 py-9">
          <div>
            <PreviewContact r={resume} />
            <PreviewSummary summary={resume.summary} />
            <PreviewWork work={resume.work_experience} />
            <PreviewEducation education={resume.education} />
            <PreviewProjects projects={resume.projects} />
            <PreviewAwards awards={resume.awards} />
            <PreviewSkills skills={resume.skills} />
            <PreviewLanguages languages={resume.languages} />
          </div>
        </div>

      </div>
    </div>
  );
}