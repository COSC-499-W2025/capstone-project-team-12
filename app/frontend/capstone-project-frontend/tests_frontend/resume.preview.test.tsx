import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import '@testing-library/jest-dom';
import ResumePreviewModal from "../src/components/resumePreviewModal";
import { downloadDocx, downloadPdf } from "../src/utils/resumeExports";
import { mockResume } from "../src/pages/resume_display";

// ─── ResumePreviewModal ───────────────────────────────────────────────────────

describe("ResumePreviewModal", () => {
  const onClose = vi.fn();

  beforeEach(() => onClose.mockClear());

  const setup = () => render(<ResumePreviewModal resume={mockResume} onClose={onClose} />);

  it("renders the preview heading", () => {
    setup();
    expect(screen.getByText("Resume Preview")).toBeInTheDocument();
  });

  it("renders the candidate name", () => {
    setup();
    expect(screen.getByText(mockResume.full_name!)).toBeInTheDocument();
  });

  it("renders contact details", () => {
    setup();
    expect(screen.getByText("github.com/yourusername", { exact: false })).toBeInTheDocument();
    expect(screen.getByText(/you@example\.com/)).toBeInTheDocument();
  });

  it("renders summary bullets", () => {
    setup();
    expect(screen.getByText(/Full-stack developer/)).toBeInTheDocument();
  });

  it("renders work experience", () => {
    setup();
    expect(screen.getByText(/UBC Okanagan/)).toBeInTheDocument();
  });

  it("renders project names", () => {
    setup();
    expect(screen.getByText(/Capstone Analysis Tool/)).toBeInTheDocument();
  });

  it("renders awards", () => {
    setup();
    expect(screen.getByText(/Test Scholars Award/)).toBeInTheDocument();
  });

  it("renders skills", () => {
    setup();
    expect(screen.getAllByText(/TypeScript/).length).toBeGreaterThan(0);
  });

  it("calls onClose when Close is clicked", () => {
    setup();
    fireEvent.click(screen.getByText("Close"));
    expect(onClose).toHaveBeenCalledOnce();
  });

  it("calls onClose when backdrop is clicked", () => {
    const { container } = setup();
    fireEvent.click(container.firstChild!);
    expect(onClose).toHaveBeenCalledOnce();
  });

  it("renders Download DOCX and Download PDF buttons", () => {
    setup();
    expect(screen.getByText("Download DOCX")).toBeInTheDocument();
    expect(screen.getByText("Download PDF ✓")).toBeInTheDocument();
  });
});

// ─── Export utilities ─────────────────────────────────────────────────────────

describe("downloadDocx", () => {
  beforeEach(() => {
    // Mock URL and anchor click so no real download fires
    vi.stubGlobal("URL", {
      createObjectURL: vi.fn(() => "blob:mock"),
      revokeObjectURL: vi.fn(),
    });
    const anchor = { href: "", download: "", click: vi.fn() };
    vi.spyOn(document, "createElement").mockImplementation((tag: string) =>
      tag === "a" ? (anchor as unknown as HTMLElement) : document.createElement(tag)
    );
  });

  afterEach(() => vi.restoreAllMocks());

  it("resolves without throwing for valid resume data", async () => {
    await expect(downloadDocx(mockResume)).resolves.toBeUndefined();
  });
});

vi.mock("html2canvas", () => ({
  default: vi.fn().mockResolvedValue({
    width: 816,
    height: 1056,
    toDataURL: () => "data:image/png;base64,abc",
  }),
}));

vi.mock("jspdf", () => ({
  jsPDF: class {
    addImage = vi.fn();
    save = vi.fn();
  },
}));

describe("downloadPdf", () => {
  it("resolves without throwing for valid resume data", async () => {
    const el = document.createElement("div");
    document.body.appendChild(el);
    await expect(downloadPdf(el)).resolves.not.toThrow();
    document.body.removeChild(el);
  });
});