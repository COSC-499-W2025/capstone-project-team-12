import { useRef, useState, useLayoutEffect } from "react";
import type { Resume } from "../types/resumeTypes";
import { downloadDocx, downloadPdf } from "../utils/resumeExports";

// ─── Preview primitives ───────────────────────────────────────────────────────

function SectionHead({ title }: { title: string }) {
  return (
    <div className="mt-3 mb-1">
      <p className="text-[10px] font-bold tracking-[0.1em] uppercase text-[#0f1629] mb-[3px]">{title}</p>
      <div className="border-b border-[#0f1629]" />
    </div>
  );
}

function TwoCol({ left, right, leftBold = false }: { left: string; right: string; leftBold?: boolean }) {
  return (
    <div className="flex justify-between items-baseline gap-2 mb-0.5">
      <span className={`text-[10.5px] text-[#0f1629] ${leftBold ? "font-bold" : "font-normal"}`}>{left}</span>
      <span className="text-[9.5px] text-[#6b7280] shrink-0">{right}</span>
    </div>
  );
}

function Bullet({ text }: { text: string }) {
  return (
    <div className="flex gap-1.5 mb-0.5">
      <span className="text-[10.5px] text-[#0f1629] shrink-0 mt-px">•</span>
      <span className="text-[10.5px] text-[#0f1629] leading-snug">{text}</span>
    </div>
  );
}

function Sub({ text, italic = false }: { text: string; italic?: boolean }) {
  return (
    <p className={`text-[10px] text-[#64748b] mb-0.5 ${italic ? "italic" : ""}`}>{text}</p>
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
    <div className="text-center mb-2">
      <p className="text-[17px] font-bold tracking-tight text-[#0f1629] mb-0.5">
        {r.full_name || r.github_username || "Resume"}
      </p>
      <p className="text-[9.5px] text-[#6b7280]">{parts.join("  |  ")}</p>
    </div>
  );
}

function PreviewSummary({ summary }: { summary: string[] }) {
  if (!summary.length) return null;
  return (
    <>
      <SectionHead title="Summary" />
      {summary.map((s, i) => <Bullet key={i} text={s} />)}
      <div className="mb-1.5" />
    </>
  );
}

function PreviewWork({ work }: { work: Resume["work_experience"] }) {
  if (!work.length) return null;
  return (
    <>
      <SectionHead title="Work Experience" />
      {work.map((w, i) => (
        <div key={i} className="mb-1.5">
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
        <div key={i} className="mb-1.5">
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
        <div key={i} className="mb-1.5">
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
        <div key={i} className="mb-1.5">
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
      <p className="text-[10.5px] text-[#0f1629] mb-1.5">{skills.join("  ·  ")}</p>
    </>
  );
}

function PreviewLanguages({ languages }: { languages: Resume["languages"] }) {
  if (!languages.length) return null;
  return (
    <>
      <SectionHead title="Programming Languages" />
      <p className="text-[10.5px] text-[#0f1629] mb-1.5">{languages.map(l => l.name).join("  ·  ")}</p>
    </>
  );
}

// ─── Overflow warning banner ──────────────────────────────────────────────────

function OverflowWarning({ overflowPx }: { overflowPx: number }) {
  return (
    <div className="flex items-center gap-2.5 bg-amber-50 border border-amber-200 rounded-xl px-4 py-2.5 w-full">
      {/* Warning icon */}
      <svg className="shrink-0 text-amber-500" width="16" height="16" viewBox="0 0 24 24" fill="none"
        stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
        <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
      </svg>
      <div className="flex-1 min-w-0">
        <p className="text-xs font-bold text-amber-700">Content exceeds one page</p>
        <p className="text-[11px] text-amber-600 mt-0.5">
          Your resume overflows by ~{Math.ceil(overflowPx / 1056 * 100)}% of a page. 
          Consider trimming bullet points or reducing entries to ensure a clean 1-page export.
        </p>
      </div>
    </div>
  );
}

// ─── Modal ────────────────────────────────────────────────────────────────────

// US Letter at 96 dpi: 8.5" × 11"
const PAGE_W = 816;
const PAGE_H = 1056;

export default function ResumePreviewModal({ resume, onClose }: { resume: Resume; onClose: () => void }) {
  const paperRef  = useRef<HTMLDivElement>(null);
  const innerRef  = useRef<HTMLDivElement>(null);
  const [overflowPx, setOverflowPx] = useState(0);
  const [busy, setBusy]             = useState<"docx" | "pdf" | null>(null);

  // Measure content height after every render; compute how much (if any) it overflows.
  useLayoutEffect(() => {
    if (!innerRef.current) return;
    const contentH = innerRef.current.scrollHeight;
    setOverflowPx(Math.max(0, contentH - PAGE_H));
  });

  const handleDocx = async () => {
    setBusy("docx");
    try   { await downloadDocx(resume); }
    catch (e) { console.error("Failed to download DOCX:", e); alert("Sorry, something went wrong while generating the DOCX file."); }
    finally   { setBusy(null); }
  };

  const handlePdf = async () => {
    if (!paperRef.current) return;
    setBusy("pdf");
    try   { await downloadPdf(paperRef.current); }
    catch (e) { console.error("Failed to download PDF:", e); alert("Sorry, something went wrong while generating the PDF."); }
    finally   { setBusy(null); }
  };

  return (
    <div onClick={onClose} className="fixed inset-0 z-50 flex items-start justify-center bg-black/50 overflow-y-auto py-10">
      <div onClick={e => e.stopPropagation()} className="flex flex-col items-center gap-4 w-max">

        {/* Toolbar */}
        <div className="flex flex-col gap-2.5 w-full bg-white rounded-xl shadow-md px-5 py-3">
          <div className="flex items-center justify-between gap-3">
            <p className="text-[11px] font-bold tracking-[0.1em] uppercase text-[#6b7280]">Resume Preview</p>
            <div className="flex items-center gap-2">
              {/* DOCX button with disclaimer tooltip wrapper */}
              <div className="relative group">
                <button onClick={handleDocx} disabled={busy !== null}
                  className="text-xs font-bold text-white bg-[#6378ff] rounded-lg px-4 py-1.5 hover:bg-indigo-700 transition-all disabled:opacity-50">
                  {busy === "docx" ? "Generating…" : "Download DOCX"}
                </button>
                {/* Tooltip */}
                <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-56 pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity z-10">
                  <div className="bg-[#0f1629] text-white text-[10px] leading-relaxed rounded-lg px-3 py-2 shadow-lg">
                    <span className="font-bold">Note:</span> DOCX page length may vary slightly depending on your version of Word or Google Docs. Use PDF for a guaranteed 1-page export.
                    <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-[#0f1629]" />
                  </div>
                </div>
              </div>
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
          {/* Persistent DOCX disclaimer strip */}
          <div className="flex items-center gap-2 bg-[#f8f9fc] border border-[#eef0f6] rounded-lg px-3 py-1.5">
            <svg className="shrink-0 text-[#6378ff]" width="12" height="12" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            <p className="text-[10.5px] text-[#6b7280]">
              <span className="font-bold text-[#0f1629]">PDF is recommended</span> for guaranteed 1-page output. 
              DOCX pagination may vary slightly across Word, LibreOffice, and Google Docs.
            </p>
          </div>
        </div>

        {/* Overflow warning — only shown when content is too tall */}
        {overflowPx > 0 && (
          <div className="w-full">
            <OverflowWarning overflowPx={overflowPx} />
          </div>
        )}

        {/* Paper — fixed 816 wide; height scrolls naturally so content is always readable */}
        <div
          ref={paperRef}
          className="shadow-2xl rounded-sm bg-white"
          style={{ width: PAGE_W }}
        >
          {/* Red dashed line at the 1-page boundary so user can see exactly where overflow starts */}
          <div className="relative">
            <div
              ref={innerRef}
              className="px-10 py-8"
              style={{ width: PAGE_W }}
            >
              <PreviewContact r={resume} />
              <PreviewSummary summary={resume.summary} />
              <PreviewWork work={resume.work_experience} />
              <PreviewEducation education={resume.education} />
              <PreviewProjects projects={resume.projects} />
              <PreviewAwards awards={resume.awards} />
              <PreviewSkills skills={resume.skills} />
              <PreviewLanguages languages={resume.languages} />
            </div>

            {/* 1-page boundary marker — only visible when there is overflow */}
            {overflowPx > 0 && (
              <div
                className="absolute left-0 right-0 pointer-events-none"
                style={{ top: PAGE_H }}
              >
                <div className="border-t-2 border-dashed border-red-400 relative">
                  <span className="absolute right-2 -top-5 text-[10px] font-bold text-red-400 bg-white px-1">
                    ↑ 1-page limit
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}