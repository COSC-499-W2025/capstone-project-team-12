import {
  Document, Packer, Paragraph, TextRun, AlignmentType,
  LevelFormat, BorderStyle,
} from "docx";
import type { Resume } from "../types/resumeTypes";

// ─── Shared layout constants ───────────────────────────────────────────────────

// US Letter: 12240 DXA wide, 15840 DXA tall
// Margins: 0.5" each side = 720 DXA  →  content width = 12240 - 2×720 = 10800 DXA
const MARGIN        = 720;   // 0.5" in DXA
const CONTENT_WIDTH = 10800; // 12240 - 2 × 720
const PAGE_W        = 12240;
const PAGE_H        = 15840;

// ─── DOCX helpers ─────────────────────────────────────────────────────────────

function sectionDivider(): Paragraph {
  return new Paragraph({
    border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "333333", space: 1 } },
    spacing: { before: 40, after: 20 },
    children: [],
  });
}

function sectionHeading(text: string): Paragraph {
  return new Paragraph({
    spacing: { before: 60, after: 20 },
    children: [new TextRun({ text: text.toUpperCase(), bold: true, size: 18, font: "Arial" })],
  });
}

function bullet(text: string): Paragraph {
  return new Paragraph({
    numbering: { reference: "resume-bullets", level: 0 },
    spacing: { before: 0, after: 10 },
    children: [new TextRun({ text, size: 18, font: "Arial" })],
  });
}

function twoColumnLine(left: string, right: string, leftBold = false): Paragraph {
  return new Paragraph({
    tabStops: [{ type: "right" as any, position: CONTENT_WIDTH }],
    spacing: { before: 0, after: 10 },
    children: [
      new TextRun({ text: left, bold: leftBold, size: 18, font: "Arial" }),
      new TextRun({ text: "\t" + right, size: 18, font: "Arial", color: "555555" }),
    ],
  });
}

function subLine(text: string, italic = false): Paragraph {
  return new Paragraph({
    spacing: { before: 0, after: 10 },
    children: [new TextRun({ text, italics: italic, size: 18, font: "Arial", color: "444444" })],
  });
}

function spacer(after = 30): Paragraph {
  return new Paragraph({ spacing: { before: 0, after }, children: [] });
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
      spacing: { before: 0, after: 25 },
      children: [new TextRun({ text: r.full_name || r.github_username || "Resume", bold: true, size: 32, font: "Arial" })],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 0, after: 20 },
      children: [new TextRun({ text: contactParts.join("  |  "), size: 17, font: "Arial", color: "444444" })],
    }),
  ];
}

function buildSummary(summary: string[]): Paragraph[] {
  if (!summary.length) return [];
  return [
    sectionHeading("Summary"),
    sectionDivider(),
    ...summary.map(s => bullet(s)),
    spacer(30),
  ];
}

function buildWorkExperience(work: Resume["work_experience"]): Paragraph[] {
  if (!work.length) return [];
  const paras: Paragraph[] = [sectionHeading("Work Experience"), sectionDivider()];
  for (const w of work) {
    paras.push(twoColumnLine(`${w.role} — ${w.company}`, w.date_range, true));
    if (w.location) paras.push(subLine(w.location, true));
    w.description.forEach(d => paras.push(bullet(d)));
    paras.push(spacer(30));
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
    paras.push(spacer(30));
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
    paras.push(spacer(30));
  }
  return paras;
}

function buildAwards(awards: Resume["awards"]): Paragraph[] {
  if (!awards.length) return [];
  const paras: Paragraph[] = [sectionHeading("Awards & Honours"), sectionDivider()];
  for (const a of awards) {
    paras.push(twoColumnLine(`${a.title} — ${a.issuer}`, a.date, true));
    a.description.forEach(d => paras.push(bullet(d)));
    paras.push(spacer(30));
  }
  return paras;
}

function buildSkills(skills: string[]): Paragraph[] {
  if (!skills.length) return [];
  return [
    sectionHeading("Skills"),
    sectionDivider(),
    new Paragraph({
      spacing: { before: 0, after: 20 },
      children: [new TextRun({ text: skills.join("  ·  "), size: 18, font: "Arial" })],
    }),
  ];
}

function buildLanguages(languages: Resume["languages"]): Paragraph[] {
  if (!languages.length) return [];
  return [
    sectionHeading("Programming Languages"),
    sectionDivider(),
    new Paragraph({
      spacing: { before: 0, after: 20 },
      children: [new TextRun({ text: languages.map(l => l.name).join("  ·  "), size: 18, font: "Arial" })],
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
          style: { paragraph: { indent: { left: 300, hanging: 150 } } },
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

/**
 * PDF export using html2canvas + jsPDF.
 *
 * Renders the live preview DOM node to a canvas at 2× device pixel ratio for
 * crisp text, then places it on a US Letter jsPDF page (816 × 1056 pt at 96 dpi).
 * The canvas is scaled to fit exactly within the page — content is never cut off,
 * and the output is always exactly 1 page.
 *
 * Requires: npm install html2canvas jspdf
 */
export async function downloadPdf(previewElement: HTMLElement): Promise<void> {
  // Dynamically import so bundle only loads these when actually needed
  const [html2canvasModule, jsPDFModule] = await Promise.all([
    import("html2canvas"),
    import("jspdf"),
  ]);
  const html2canvas = html2canvasModule.default;
  const { jsPDF }   = jsPDFModule;

  // The preview element is 816 × 1056px (our "paper" div).
  // Its first child may have a CSS scale transform for the preview — remove it
  // temporarily so html2canvas captures full-resolution glyphs.
  const innerContent = previewElement.firstElementChild as HTMLElement | null;
  const savedTransform = innerContent?.style.transform ?? "";
  const savedOverflow  = previewElement.style.overflow;

  if (innerContent) innerContent.style.transform = "none";
  previewElement.style.overflow = "visible"; // allow html2canvas to capture full height

  try {
    const canvas = await html2canvas(previewElement, {
      scale: 2,           // 2× for retina-quality text
      useCORS: true,
      logging: false,
      backgroundColor: "#ffffff",
      // Capture at the element's natural scroll dimensions so nothing is clipped
      width:  previewElement.scrollWidth,
      height: previewElement.scrollHeight,
      windowWidth:  previewElement.scrollWidth,
      windowHeight: previewElement.scrollHeight,
    });

    // US Letter in points at 72dpi: 612 × 792 pt
    // html2canvas produces pixels; we map them onto the page proportionally.
    const PDF_W_PT = 612;
    const PDF_H_PT = 792;

    const imgW = canvas.width;
    const imgH = canvas.height;

    // Scale image to fit page width; if it's taller than one page, scale to fit height.
    const scaleByWidth  = PDF_W_PT / imgW;
    const scaleByHeight = PDF_H_PT / imgH;
    const scale         = Math.min(scaleByWidth, scaleByHeight);

    const drawW = imgW * scale;
    const drawH = imgH * scale;

    // Center on the page
    const offsetX = (PDF_W_PT - drawW) / 2;
    const offsetY = (PDF_H_PT - drawH) / 2;

    const pdf = new jsPDF({
      orientation: "portrait",
      unit: "pt",
      format: "letter",
    });

    pdf.addImage(
      canvas.toDataURL("image/png"),
      "PNG",
      offsetX,
      offsetY,
      drawW,
      drawH,
    );

    pdf.save("resume.pdf");
  } finally {
    // Always restore styles even if export fails
    if (innerContent) innerContent.style.transform = savedTransform;
    previewElement.style.overflow = savedOverflow;
  }
}

function triggerDownload(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const a   = document.createElement("a");
  a.href    = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}