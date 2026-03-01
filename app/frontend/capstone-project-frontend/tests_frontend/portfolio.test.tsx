import { render, screen, fireEvent, within } from "@testing-library/react";
import { describe, it, expect, beforeEach, vi } from "vitest";
import Portfolio from "../src/pages/Portfolio";

// ─── MOCK DATA ───────────────────────────────────────────────────────────────
// Minimal but realistic — mirrors the real data shape
const mockData = {
  developer: "Jane Doe",
  coreCompetencies: ["Web Development", "Backend Development"],
  languages: [
    { name: "JavaScript", pct: 55.0, files: 30 },
    { name: "Python",     pct: 45.0, files: 24 },
  ],
  projects: [
    {
      id: 1,
      name: "my-cool-project",
      timeline: "Jan 2025 – Mar 2025",
      duration: "60 days",
      role: "Lead Developer",
      insight: "Primary contributor with broad impact across the codebase.",
      contribution: { level: "Top Contributor", teamSize: 3, rank: 1, percentile: 100, share: 72.0 },
      totals: { commits: 50, files: 200, added: 8000, deleted: 1000, net: 7000 },
      mine:   { commits: 36, added: 5800, deleted: 700, net: 5100, files: 140 },
      technologies: ["react", "node.js", "postgresql"],
    },
    {
      id: 2,
      name: "team-project-alpha",
      timeline: "Mar 2025 – Apr 2025",
      duration: "30 days",
      role: "Feature Developer",
      insight: "Focused contributions on key features.",
      contribution: { level: "Significant Contributor", teamSize: 5, rank: 2, percentile: 75, share: 20.0 },
      totals: { commits: 80, files: 300, added: 12000, deleted: 2000, net: 10000 },
      mine:   { commits: 16, added: 2400, deleted: 400, net: 2000, files: 60 },
      technologies: [],
    },
  ],
};

// ─── INTERSECTION OBSERVER MOCK ──────────────────────────────────────────────
// jsdom doesn't implement IntersectionObserver — we need to mock it.
// This mock immediately fires the callback so animated elements become visible.
beforeEach(() => {
  window.IntersectionObserver = class IntersectionObserver {
    root = null;
    rootMargin = '';
    thresholds = [];
    callback: IntersectionObserverCallback;
    constructor(callback: IntersectionObserverCallback) {
      this.callback = callback;
    }
    observe() {
      this.callback([{ isIntersecting: true } as IntersectionObserverEntry], this);
    }
    disconnect() {}
    unobserve() {}
    takeRecords() { return []; }
  };
});

// ─── TESTS ───────────────────────────────────────────────────────────────────

describe("Portfolio — hero section", () => {
  it("renders the developer name", () => {
    render(<Portfolio data={mockData} />);
    expect(screen.getByText("Jane Doe")).toBeInTheDocument();
  });

  it("renders all core competencies", () => {
    render(<Portfolio data={mockData} />);
    expect(screen.getByText("Web Development")).toBeInTheDocument();
    expect(screen.getByText("Backend Development")).toBeInTheDocument();
  });

  it("shows the correct project count", () => {
    render(<Portfolio data={mockData} />);
    // The big number in the hero should equal projects.length
    expect(screen.getByText("2")).toBeInTheDocument();
  });
});

describe("Portfolio — project cards", () => {
  it("renders all project names", () => {
    render(<Portfolio data={mockData} />);
    expect(screen.getByText("my-cool-project")).toBeInTheDocument();
    expect(screen.getByText("team-project-alpha")).toBeInTheDocument();
  });

  it("renders timeline and duration for each project", () => {
    render(<Portfolio data={mockData} />);
    expect(screen.getByText(/Jan 2025 – Mar 2025/)).toBeInTheDocument();
    expect(screen.getByText(/60 days/)).toBeInTheDocument();
  });

  it("renders the role tag", () => {
    render(<Portfolio data={mockData} />);
    expect(screen.getByText("Lead Developer")).toBeInTheDocument();
    expect(screen.getByText("Feature Developer")).toBeInTheDocument();
  });

  it("renders the insight text", () => {
    render(<Portfolio data={mockData} />);
    expect(screen.getByText("Primary contributor with broad impact across the codebase.")).toBeInTheDocument();
  });
});

describe("Portfolio — contribution hero", () => {
  it("displays rank correctly as #1/3 and #2/5", () => {
    render(<Portfolio data={mockData} />);
    expect(screen.getAllByText("#1").length).toBeGreaterThan(0);
    expect(screen.getAllByText("#2").length).toBeGreaterThan(0);
    expect(screen.getAllByText("/3").length).toBeGreaterThan(0);
    expect(screen.getAllByText("/5").length).toBeGreaterThan(0);
  });

  it("displays commit share percentages", () => {
    render(<Portfolio data={mockData} />);
    expect(screen.getByText("72%")).toBeInTheDocument();
    expect(screen.getByText("20%")).toBeInTheDocument();
  });

  it("displays contribution level labels", () => {
    render(<Portfolio data={mockData} />);
    expect(screen.getAllByText("Top Contributor").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Significant Contributor").length).toBeGreaterThan(0);
  });
});

describe("Portfolio — expandable card", () => {
  it("project totals section is hidden before clicking", () => {
    render(<Portfolio data={mockData} />);
    // The expandable div has maxHeight: 0 — PROJECT TOTALS text still exists
    // in the DOM but the section should not be visible (maxHeight 0)
    const expandables = document.querySelectorAll("[style*='max-height: 0']");
    expect(expandables.length).toBeGreaterThan(0);
  });

  it("collapses again when header is clicked a second time", () => {
    render(<Portfolio data={mockData} />);
    const header = screen.getByText("my-cool-project");
    fireEvent.click(header); // open
    fireEvent.click(header); // close
    const expandables = document.querySelectorAll("[style*='max-height: 0']");
    expect(expandables.length).toBeGreaterThan(0);
  });

  it("shows technologies when expanded (project with techs)", () => {
    render(<Portfolio data={mockData} />);
    fireEvent.click(screen.getByText("my-cool-project"));
    expect(screen.getByText("react")).toBeInTheDocument();
    expect(screen.getByText("node.js")).toBeInTheDocument();
    expect(screen.getByText("postgresql")).toBeInTheDocument();
  });
});

describe("Portfolio — language bars", () => {
  it("renders all language names", () => {
    render(<Portfolio data={mockData} />);
    expect(screen.getByText("JavaScript")).toBeInTheDocument();
    expect(screen.getByText("Python")).toBeInTheDocument();
  });

  it("renders language percentages correctly formatted", () => {
    render(<Portfolio data={mockData} />);
    expect(screen.getByText("55.0%")).toBeInTheDocument();
    expect(screen.getByText("45.0%")).toBeInTheDocument();
  });

  it("renders file counts", () => {
    render(<Portfolio data={mockData} />);
    expect(screen.getByText("30 files")).toBeInTheDocument();
    expect(screen.getByText("24 files")).toBeInTheDocument();
  });
});

describe("Portfolio — data prop", () => {
  it("renders with different developer name", () => {
    const data = { ...mockData, developer: "John Smith" };
    render(<Portfolio data={data} />);
    expect(screen.getByText("John Smith")).toBeInTheDocument();
  });

  it("renders with a single project", () => {
    const data = { ...mockData, projects: [mockData.projects[0]] };
    render(<Portfolio data={data} />);
    expect(screen.queryByText("team-project-alpha")).not.toBeInTheDocument();
    expect(screen.getByText("my-cool-project")).toBeInTheDocument();
  });

  it("renders with no languages gracefully", () => {
    const data = { ...mockData, languages: [] };
    render(<Portfolio data={data} />);
    expect(screen.getByText("Language Proficiency")).toBeInTheDocument();
  });
});