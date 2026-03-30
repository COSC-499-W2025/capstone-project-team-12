import {
  Document, Packer, Paragraph, TextRun, AlignmentType,
  LevelFormat, BorderStyle,
} from "docx";
import type { Resume } from "../types/resumeTypes";

// ─── Shared layout constants ───────────────────────────────────────────────────

const CONTENT_WIDTH = 9360; // DXA — US Letter (12240) minus 1" margins each side (1440 × 2)
const MARGIN        = 864;  // 0.6" margins (a bit tighter for one-page fit)
const PAGE_W        = 12240;
const PAGE_H        = 15840;

// ─── DOCX helpers ─────────────────────────────────────────────────────────────

function sectionDivider(): Paragraph {
  return new Paragraph({
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "333333", space: 1 } },
    spacing: { before: 100, after: 60 },
    children: [],
  });
}

function sectionHeading(text: string): Paragraph {
  return new Paragraph({
    spacing: { before: 120, after: 40 },
    children: [new TextRun({ text: text.toUpperCase(), bold: true, size: 22, font: "Arial" })],
  });
}

function bullet(text: string): Paragraph {
  return new Paragraph({
    numbering: { reference: "resume-bullets", level: 0 },
    spacing: { before: 0, after: 20 },
    children: [new TextRun({ text, size: 20, font: "Arial" })],
  });
}

function twoColumnLine(left: string, right: string, leftBold = false): Paragraph {
  return new Paragraph({
    tabStops: [{ type: "right" as any, position: CONTENT_WIDTH }],
    spacing: { before: 0, after: 20 },
    children: [
      new TextRun({ text: left, bold: leftBold, size: 20, font: "Arial" }),
      new TextRun({ text: "\t" + right, size: 20, font: "Arial", color: "555555" }),
    ],
  });
}

function subLine(text: string, italic = false): Paragraph {
  return new Paragraph({
    spacing: { before: 0, after: 20 },
    children: [new TextRun({ text, italics: italic, size: 20, font: "Arial", color: "444444" })],
  });
}

// ─── Section builders ─────────────────────────────────────────────────────────

function buildContact(r: Resume): Paragraph[] {
  const contactParts: string[] = [];
  if (r.user_email)      contactParts.push(r.user_email);
  if (r.github_username) contactParts.push(`github.com/${r.github_username}`);
  if (r.phone)           contactParts.push(r.phone);
  if (r.linkedin)        contactParts.push(r.linkedin);

  return [
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 0, after: 60 },
      children: [new TextRun({ text: r.full_name || r.github_username || "Resume", bold: true, size: 36, font: "Arial" })],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 0, after: 40 },
      children: [new TextRun({ text: contactParts.join("  |  "), size: 19, font: "Arial", color: "444444" })],
    }),
  ];
}

function buildSummary(summary: string[]): Paragraph[] {
  if (!summary.length) return [];
  return [
    sectionHeading("Summary"),
    sectionDivider(),
    ...summary.map(s => bullet(s)),
  ];
}

function buildWorkExperience(work: Resume["work_experience"]): Paragraph[] {
  if (!work.length) return [];
  const paras: Paragraph[] = [sectionHeading("Work Experience"), sectionDivider()];
  for (const w of work) {
    paras.push(twoColumnLine(`${w.role} — ${w.company}`, w.date_range, true));
    if (w.location) paras.push(subLine(w.location, true));
    w.description.forEach(d => paras.push(bullet(d)));
    paras.push(new Paragraph({ spacing: { before: 0, after: 60 }, children: [] }));
  }
  return paras;
}

function buildEducation(education: Resume["education"]): Paragraph[] {
  if (!education.length) return [];
  const paras: Paragraph[] = [sectionHeading("Education"), sectionDivider()];
  for (const e of education) {
    paras.push(twoColumnLine(e.institution, e.date_range, true));
    const degreeStr = [e.degree, e.major ? `Major in ${e.major}` : "", e.minor ? `Minor in ${e.minor}` : ""].filter(Boolean).join(" · ");
    paras.push(subLine(degreeStr));
    if (e.notes) paras.push(subLine(e.notes, true));
    paras.push(new Paragraph({ spacing: { before: 0, after: 60 }, children: [] }));
  }
  return paras;
}

function buildProjects(projects: Resume["projects"]): Paragraph[] {
  if (!projects.length) return [];
  const paras: Paragraph[] = [sectionHeading("Projects"), sectionDivider()];
  for (const p of projects) {
    paras.push(twoColumnLine(p.name, p.date_range, true));
    if (p.frameworks.length) paras.push(subLine(`Technologies: ${p.frameworks.join(", ")}`));
    paras.push(bullet(p.collaboration));
    paras.push(new Paragraph({ spacing: { before: 0, after: 60 }, children: [] }));
  }
  return paras;
}

function buildAwards(awards: Resume["awards"]): Paragraph[] {
  if (!awards.length) return [];
  const paras: Paragraph[] = [sectionHeading("Awards & Honours"), sectionDivider()];
  for (const a of awards) {
    paras.push(twoColumnLine(`${a.title} — ${a.issuer}`, a.date, true));
    a.description.forEach(d => paras.push(bullet(d)));
    paras.push(new Paragraph({ spacing: { before: 0, after: 60 }, children: [] }));
  }
  return paras;
}

function buildSkills(skills: string[]): Paragraph[] {
  if (!skills.length) return [];
  return [
    sectionHeading("Skills"),
    sectionDivider(),
    new Paragraph({
      spacing: { before: 0, after: 60 },
      children: [new TextRun({ text: skills.join("  ·  "), size: 20, font: "Arial" })],
    }),
  ];
}

function buildLanguages(languages: Resume["languages"]): Paragraph[] {
  if (!languages.length) return [];
  return [
    sectionHeading("Programming Languages"),
    sectionDivider(),
    new Paragraph({
      spacing: { before: 0, after: 60 },
      children: [new TextRun({ text: languages.map(l => l.name).join("  ·  "), size: 20, font: "Arial" })],
    }),
  ];
}

// ─── Public API ───────────────────────────────────────────────────────────────

export async function downloadDocx(resume: Resume): Promise<void> {
  const doc = new Document({
    numbering: {
      config: [{
        reference: "resume-bullets",
        levels: [{
          level: 0,
          format: LevelFormat.BULLET,
          text: "\u2022",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 360, hanging: 180 } } },
        }],
      }],
    },
    sections: [{
      properties: {
        page: {
          size: { width: PAGE_W, height: PAGE_H },
          margin: { top: MARGIN, right: MARGIN, bottom: MARGIN, left: MARGIN },
        },
      },
      children: [
        ...buildContact(resume),
        ...buildSummary(resume.summary),
        ...buildWorkExperience(resume.work_experience),
        ...buildEducation(resume.education),
        ...buildProjects(resume.projects),
        ...buildAwards(resume.awards),
        ...buildSkills(resume.skills),
        ...buildLanguages(resume.languages),
      ],
    }],
  });
  const blob = await Packer.toBlob(doc);
  triggerDownload(blob, "resume.docx");
}

export function downloadPdf(previewElement: HTMLElement): void {
  const LETTER_HEIGHT_PX = 1056;
  const PADDING = 48; // px on each side
  const scale = Math.min(1, LETTER_HEIGHT_PX / previewElement.scrollHeight);

  const clone = document.createElement("div");
  clone.id = "resume-print-target";
  clone.style.cssText = `
    position: absolute;
    top: 0;
    left: 0;
    width: 816px;
    background: white;
    padding: ${PADDING}px;
    box-sizing: border-box;
    transform-origin: top left;
    transform: scale(${scale});
  `;
  clone.innerHTML = previewElement.innerHTML;
  document.body.appendChild(clone);

  const style = document.createElement("style");
  style.textContent = `
    @media print {
      body > * { display: none !important; }
      #resume-print-target { display: block !important; }
      @page { margin: 0; size: letter portrait; }
    }
  `;
  document.head.appendChild(style);
  window.print();
  document.head.removeChild(style);
  document.body.removeChild(clone);
}

function triggerDownload(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const a   = document.createElement("a");
  a.href    = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}