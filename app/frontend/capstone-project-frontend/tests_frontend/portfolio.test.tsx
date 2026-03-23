import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import "@testing-library/jest-dom";
import DevPortfolio from "../src/pages/Portfolio";

// ─── MOCK DATA ───────────────────────────────────────────────────────────────
// Mirrors the raw API response shape that fetchPortfolio normalises.
const mockApiResponse = {
  portfolio_title: "Jane Doe",
  portfolio_data: {
    result_id: "00000000-0000-0000-0000-000000000000",
    skill_timeline: {
      high_level_skills: ["Web Development", "Backend Development"],
      language_progression: [
        { name: "JavaScript", percentage: 55.0, file_count: 30 },
        { name: "Python",     percentage: 45.0, file_count: 24 },
      ],
      framework_timeline_list: [],
    },
    projects_detail: [
      {
        name: "my-cool-project",
        date_range: "Jan 2025 – Mar 2025",
        duration_days: 60,
        user_role: { role: "Lead Developer", blurb: "Primary contributor with broad impact across the codebase." },
        contribution: { level: "Top Contributor", team_size: 3, rank: 1, percentile: 100, contribution_share: 72.0 },
        statistics: {
          commits: 50, files: 200, additions: 8000, deletions: 1000, net_lines: 7000,
          user_commits: 36, user_lines_added: 5800, user_lines_deleted: 700, user_net_lines: 5100, user_files_modified: 140,
        },
        frameworks_summary: { top_frameworks: ["react", "node.js", "postgresql"] },
      },
      {
        name: "team-project-alpha",
        date_range: "Mar 2025 – Apr 2025",
        duration_days: 30,
        user_role: { role: "Feature Developer", blurb: "Focused contributions on key features." },
        contribution: { level: "Significant Contributor", team_size: 5, rank: 2, percentile: 75, contribution_share: 20.0 },
        statistics: {
          commits: 80, files: 300, additions: 12000, deletions: 2000, net_lines: 10000,
          user_commits: 16, user_lines_added: 2400, user_lines_deleted: 400, user_net_lines: 2000, user_files_modified: 60,
        },
        frameworks_summary: { top_frameworks: [] },
      },
    ],
    growth_metrics: null,
  },
};

// ─── INTERSECTION OBSERVER MOCK ──────────────────────────────────────────────
beforeEach(() => {
  window.IntersectionObserver = class IntersectionObserver {
    root = null;
    rootMargin = "";
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

afterEach(() => {
  vi.restoreAllMocks();
});

// ─── HELPERS ─────────────────────────────────────────────────────────────────

function mockFetch(response = mockApiResponse) {
  vi.spyOn(globalThis, "fetch").mockResolvedValue({
    ok: true,
    json: async () => response,
  } as Response);
}

async function renderLoaded(response = mockApiResponse, waitForText = "Jane Doe") {
  mockFetch(response);
  render(<DevPortfolio portfolioId={1} />);
  await screen.findByText(waitForText);
}

// Edit tests use a single-project response with no title so "Untitled Portfolio" renders.
async function renderEditing() {
  mockFetch({
    ...mockApiResponse,
    portfolio_title: "",
    portfolio_data: {
      ...mockApiResponse.portfolio_data,
      projects_detail: [mockApiResponse.portfolio_data.projects_detail[0]],
    },
  });
  render(<DevPortfolio portfolioId={1} />);
  await screen.findByText("Untitled Portfolio");
}

// ─── HERO SECTION ────────────────────────────────────────────────────────────

describe("Portfolio — hero section", () => {
  it("renders the developer name", async () => {
    await renderLoaded();
    expect(screen.getByText("Jane Doe")).toBeInTheDocument();
  });

  it("renders all core competencies", async () => {
    await renderLoaded();
    expect(screen.getByText("Web Development")).toBeInTheDocument();
    expect(screen.getByText("Backend Development")).toBeInTheDocument();
  });

  it("shows the correct project count", async () => {
    await renderLoaded();
    expect(screen.getByText("2")).toBeInTheDocument();
  });
});

// ─── PROJECT CARDS ───────────────────────────────────────────────────────────

describe("Portfolio — project cards", () => {
  it("renders all project names", async () => {
    await renderLoaded();
    expect(screen.getByText("my-cool-project")).toBeInTheDocument();
    expect(screen.getByText("team-project-alpha")).toBeInTheDocument();
  });

  it("renders timeline and duration for each project", async () => {
    await renderLoaded();
    expect(screen.getByText(/Jan 2025 – Mar 2025/)).toBeInTheDocument();
    expect(screen.getByText(/60 days/)).toBeInTheDocument();
  });

  it("renders the role tag", async () => {
    await renderLoaded();
    expect(screen.getByText("Lead Developer")).toBeInTheDocument();
    expect(screen.getByText("Feature Developer")).toBeInTheDocument();
  });

  it("renders the insight text", async () => {
    await renderLoaded();
    expect(screen.getByText("Primary contributor with broad impact across the codebase.")).toBeInTheDocument();
  });
});

// ─── CONTRIBUTION HERO ───────────────────────────────────────────────────────

describe("Portfolio — contribution hero", () => {
  it("displays rank correctly as #1/3 and #2/5", async () => {
    await renderLoaded();
    expect(screen.getAllByText("#1").length).toBeGreaterThan(0);
    expect(screen.getAllByText("#2").length).toBeGreaterThan(0);
    expect(screen.getAllByText("/3").length).toBeGreaterThan(0);
    expect(screen.getAllByText("/5").length).toBeGreaterThan(0);
  });

  it("displays commit share percentages", async () => {
    await renderLoaded();
    expect(screen.getByText("72%")).toBeInTheDocument();
    expect(screen.getByText("20%")).toBeInTheDocument();
  });

  it("displays contribution level labels", async () => {
    await renderLoaded();
    expect(screen.getAllByText("Top Contributor").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Significant Contributor").length).toBeGreaterThan(0);
  });
});

// ─── EXPANDABLE CARD ─────────────────────────────────────────────────────────

describe("Portfolio — expandable card", () => {
  it("project totals section is hidden before clicking", async () => {
    await renderLoaded();
    const expandables = document.querySelectorAll("[style*='max-height: 0']");
    expect(expandables.length).toBeGreaterThan(0);
  });

  it("collapses again when header is clicked a second time", async () => {
    await renderLoaded();
    const header = screen.getByText("my-cool-project");
    fireEvent.click(header); // open
    fireEvent.click(header); // close
    const expandables = document.querySelectorAll("[style*='max-height: 0']");
    expect(expandables.length).toBeGreaterThan(0);
  });

  it("shows technologies when expanded (project with techs)", async () => {
    await renderLoaded();
    fireEvent.click(screen.getByText("my-cool-project"));
    expect(screen.getByText("react")).toBeInTheDocument();
    expect(screen.getByText("node.js")).toBeInTheDocument();
    expect(screen.getByText("postgresql")).toBeInTheDocument();
  });
});

// ─── LANGUAGE BARS ───────────────────────────────────────────────────────────

describe("Portfolio — language bars", () => {
  it("renders all language names", async () => {
    await renderLoaded();
    expect(screen.getByText("JavaScript")).toBeInTheDocument();
    expect(screen.getByText("Python")).toBeInTheDocument();
  });

  it("renders language percentages correctly formatted", async () => {
    await renderLoaded();
    expect(screen.getByText("55.0%")).toBeInTheDocument();
    expect(screen.getByText("45.0%")).toBeInTheDocument();
  });

  it("renders file counts", async () => {
    await renderLoaded();
    expect(screen.getByText("30 files")).toBeInTheDocument();
    expect(screen.getByText("24 files")).toBeInTheDocument();
  });
});

// ─── RESPONSE VARIANTS ───────────────────────────────────────────────────────

describe("Portfolio — response variants", () => {
  it("renders with a different developer name", async () => {
    await renderLoaded({
      ...mockApiResponse,
      portfolio_title: "John Smith",
    }, "John Smith");
    expect(screen.getByText("John Smith")).toBeInTheDocument();
  });

  it("renders with a single project", async () => {
    await renderLoaded({
      ...mockApiResponse,
      portfolio_data: {
        ...mockApiResponse.portfolio_data,
        projects_detail: [mockApiResponse.portfolio_data.projects_detail[0]],
      },
    }, "my-cool-project");
    expect(screen.getByText("my-cool-project")).toBeInTheDocument();
    expect(screen.queryByText("team-project-alpha")).not.toBeInTheDocument();
  });

  it("renders with no languages gracefully", async () => {
    await renderLoaded({
      ...mockApiResponse,
      portfolio_data: {
        ...mockApiResponse.portfolio_data,
        skill_timeline: { ...mockApiResponse.portfolio_data.skill_timeline, language_progression: [] },
      },
    }, "Language Proficiency");
    expect(screen.getByText("Language Proficiency")).toBeInTheDocument();
  });
});

// ─── EDIT: HEADER ────────────────────────────────────────────────────────────

describe("Portfolio — edit header", () => {
  it("enters edit mode and saves new title", async () => {
    await renderEditing();
    fireEvent.click(screen.getByRole("button", { name: "Edit header" }));
    fireEvent.change(screen.getByPlaceholderText("Enter Portfolio name"), { target: { value: "My Portfolio" } });
    fireEvent.click(screen.getByRole("button", { name: "Save header" }));
    expect(screen.getByText("My Portfolio")).toBeInTheDocument();
  });

  it("discards changes on cancel", async () => {
    await renderEditing();
    fireEvent.click(screen.getByRole("button", { name: "Edit header" }));
    fireEvent.change(screen.getByPlaceholderText("Enter Portfolio name"), { target: { value: "Discarded" } });
    fireEvent.click(screen.getByRole("button", { name: "Cancel header" }));
    expect(screen.queryByText("Discarded")).not.toBeInTheDocument();
  });

  it("can remove a competency and save", async () => {
    await renderEditing();
    fireEvent.click(screen.getByRole("button", { name: "Edit header" }));
    fireEvent.click(screen.getAllByText("×")[0]);
    fireEvent.click(screen.getByRole("button", { name: "Save header" }));
    await waitFor(() => expect(screen.queryByText("Web Development")).not.toBeInTheDocument());
  });
});

// ─── EDIT: LANGUAGES ─────────────────────────────────────────────────────────

describe("Portfolio — edit languages", () => {
  it("can remove a language and save", async () => {
    await renderEditing();
    fireEvent.click(screen.getByRole("button", { name: "Edit languages" }));
    fireEvent.click(screen.getAllByText("×")[0]);
    fireEvent.click(screen.getByRole("button", { name: "Save languages" }));
    await waitFor(() => expect(screen.queryByText("JavaScript")).not.toBeInTheDocument());
  });

  it("discards changes on cancel", async () => {
    await renderEditing();
    fireEvent.click(screen.getByRole("button", { name: "Edit languages" }));
    fireEvent.click(screen.getAllByText("×")[0]);
    fireEvent.click(screen.getByRole("button", { name: "Cancel languages" }));
    expect(screen.getByText("JavaScript")).toBeInTheDocument();
  });
});

// ─── EDIT: PROJECTS ──────────────────────────────────────────────────────────

describe("Portfolio — edit projects", () => {
  it("saves updated project name", async () => {
    await renderEditing();
    fireEvent.click(screen.getByRole("button", { name: "Edit project 0" }));
    fireEvent.change(screen.getByDisplayValue("my-cool-project"), { target: { value: "renamed-project" } });
    fireEvent.click(screen.getByRole("button", { name: "Save project 0" }));
    await waitFor(() => expect(screen.getByText("renamed-project")).toBeInTheDocument());
  });

  it("discards changes on cancel", async () => {
    await renderEditing();
    fireEvent.click(screen.getByRole("button", { name: "Edit project 0" }));
    fireEvent.change(screen.getByDisplayValue("my-cool-project"), { target: { value: "should-not-appear" } });
    fireEvent.click(screen.getByRole("button", { name: "Cancel project 0" }));
    expect(screen.queryByText("should-not-appear")).not.toBeInTheDocument();
  });
});