import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import "@testing-library/jest-dom";
import DevPortfolio from "../src/pages/Portfolio";

// ─── MOCK DATA ───────────────────────────────────────────────────────────────
// Mirrors the raw API response shape that fetchPortfolio expects
const mockApiResponse = {
  portfolio_data: {
    result_id: "Jane Doe",
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

function makeFetchMock(apiResponse = mockApiResponse) {
  return vi.fn(() =>
    Promise.resolve({
      ok: true,
      json: async () => apiResponse,
    } as Response)
  );
}
// Minimal but realistic — mirrors the real data shape
const mockData = {
  title: "Jane Doe",
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

// ─── HELPER ──────────────────────────────────────────────────────────────────

async function renderLoaded(apiResponse = mockApiResponse) {
  vi.spyOn(globalThis, "fetch").mockImplementation(makeFetchMock(apiResponse));
  render(<DevPortfolio portfolioId={1} />);
  // Wait for the async fetch to resolve and data to render
  await screen.findByText("Jane Doe");
}

// ─── TESTS ───────────────────────────────────────────────────────────────────

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

describe("Portfolio — data prop", () => {
  it("renders with different developer name", async () => {
    const customResponse = {
      portfolio_data: {
        ...mockApiResponse.portfolio_data,
        result_id: "John Smith",
      },
    };
    vi.spyOn(globalThis, "fetch").mockImplementation(makeFetchMock(customResponse));
    render(<DevPortfolio portfolioId={1} />);
    await screen.findByText("John Smith");
    expect(screen.getByText("John Smith")).toBeInTheDocument();
  });

  it("renders with a single project", async () => {
    const customResponse = {
      portfolio_data: {
        ...mockApiResponse.portfolio_data,
        projects_detail: [mockApiResponse.portfolio_data.projects_detail[0]],
      },
    };
    vi.spyOn(globalThis, "fetch").mockImplementation(makeFetchMock(customResponse));
    render(<DevPortfolio portfolioId={1} />);
    await screen.findByText("my-cool-project");
    expect(screen.queryByText("team-project-alpha")).not.toBeInTheDocument();
    expect(screen.getByText("my-cool-project")).toBeInTheDocument();
  });

  it("renders with no languages gracefully", async () => {
    const customResponse = {
      portfolio_data: {
        ...mockApiResponse.portfolio_data,
        skill_timeline: {
          ...mockApiResponse.portfolio_data.skill_timeline,
          language_progression: [],
        },
      },
    };
    vi.spyOn(globalThis, "fetch").mockImplementation(makeFetchMock(customResponse));
    render(<DevPortfolio portfolioId={1} />);
    await screen.findByText("Jane Doe");
    expect(screen.getByText("Language Proficiency")).toBeInTheDocument();
  });
});

// ─── EDIT TESTS SETUP ────────────────────────────────────────────────────────

const mockApiResponse = {
  portfolio_title: null,
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
    projects_detail: [{
      name: "my-cool-project",
      date_range: "Jan 2025 – Mar 2025",
      duration_days: 60,
      user_role: { role: "Lead Developer", blurb: "Primary contributor." },
      contribution: { level: "Top Contributor", team_size: 3, rank: 1, percentile: 100, contribution_share: 72.0 },
      statistics: {
        commits: 50, files: 200, additions: 8000, deletions: 1000, net_lines: 7000,
        user_commits: 36, user_lines_added: 5800, user_lines_deleted: 700, user_net_lines: 5100, user_files_modified: 140,
      },
      frameworks_summary: { top_frameworks: ["react", "node.js"] },
    }],
    growth_metrics: null,
  },
};

async function renderEditing() {
  vi.spyOn(globalThis, "fetch").mockImplementation(() =>
    Promise.resolve({ ok: true, json: async () => mockApiResponse } as Response)
  );
  render(<Portfolio portfolioId={1} />);
  await screen.findByText("Untitled Portfolio");
}

// ─── EDITING ─────────────────────────────────────────────────────────────────

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