import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import "@testing-library/jest-dom";
import { MemoryRouter } from "react-router-dom";
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
    growth_metrics: null as any,
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
  render(<MemoryRouter><DevPortfolio portfolioId={1} /></MemoryRouter>);
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
  render(<MemoryRouter><DevPortfolio portfolioId={1} /></MemoryRouter>);
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

describe("Portfolio: edit header", () => {
  it("enters edit mode and saves new title", async () => {
    await renderEditing();
    fireEvent.click(screen.getByRole("button", { name: "Edit header" }));

    fireEvent.change(
      screen.getByPlaceholderText("Enter Portfolio name"),
      { target: { value: "My Portfolio" } }
    );

    fireEvent.click(screen.getByRole("button", { name: "Save header" }));
    expect(await screen.findByText("My Portfolio")).toBeInTheDocument();
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

// ─── PUBLIC / PRIVATE MODE ───────────────────────────────────────────────────

describe("Portfolio — mode toggle", () => {
  it("renders the Public button by default (private mode active)", async () => {
    await renderLoaded();
    expect(screen.getByTitle(/Switch to Public/i)).toBeInTheDocument();
  });

  it("switches to public mode and shows Private button", async () => {
    await renderLoaded();
    fireEvent.click(screen.getByTitle(/Switch to Public/i));
    expect(screen.getByTitle(/Switch to Private/i)).toBeInTheDocument();
  });

  it("hides Edit buttons when in public mode", async () => {
    await renderLoaded();
    fireEvent.click(screen.getByTitle(/Switch to Public/i));
    expect(screen.queryByRole("button", { name: /Edit header/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Edit languages/i })).not.toBeInTheDocument();
  });

  it("shows Edit buttons when back in private mode", async () => {
    await renderLoaded();
    fireEvent.click(screen.getByTitle(/Switch to Public/i));
    fireEvent.click(screen.getByTitle(/Switch to Private/i));
    expect(screen.getByRole("button", { name: /Edit header/i })).toBeInTheDocument();
  });
});

// ─── PUBLIC MODE: SEARCH ─────────────────────────────────────────────────────

describe("Portfolio — search (public mode)", () => {
  async function goPublic() {
    await renderLoaded();
    fireEvent.click(screen.getByTitle(/Switch to Public/i));
  }

  it("filters project cards by name", async () => {
    await goPublic();
    fireEvent.change(
      screen.getByPlaceholderText(/Search projects/i),
      { target: { value: "my-cool-project" } }
    );
    expect(screen.getAllByText("my-cool-project").length).toBeGreaterThan(0);
    // team-project-alpha should only exist as the filter chip, not as a card
    const remaining = screen.getAllByText("team-project-alpha");
    expect(remaining).toHaveLength(1);
    expect(remaining[0].closest("button")).toBeInTheDocument(); // it's the chip
  });

  it("filters language bars by name", async () => {
    await goPublic();
    fireEvent.change(
      screen.getByPlaceholderText(/Search projects/i),
      { target: { value: "Python" } }
    );
    expect(screen.getByText("Python")).toBeInTheDocument();
    expect(screen.queryByText("JavaScript")).not.toBeInTheDocument();
  });

  it("shows empty state when no project matches the query", async () => {
    await goPublic();
    fireEvent.change(
      screen.getByPlaceholderText(/Search projects/i),
      { target: { value: "zzznomatch" } }
    );
    expect(screen.getByText(/No projects match your search/i)).toBeInTheDocument();
  });

  it("clears search query when switching back to private mode", async () => {
    await goPublic();
    fireEvent.change(
      screen.getByPlaceholderText(/Search projects/i),
      { target: { value: "my-cool-project" } }
    );
    fireEvent.click(screen.getByTitle(/Switch to Private/i));
    // Both projects should be visible again
    expect(screen.getByText("my-cool-project")).toBeInTheDocument();
    expect(screen.getByText("team-project-alpha")).toBeInTheDocument();
  });
});

// ─── PUBLIC MODE: FILTER CHIPS ────────────────────────────────────────────────

describe("Portfolio — filter chips (public mode)", () => {
  async function goPublic() {
    await renderLoaded();
    fireEvent.click(screen.getByTitle(/Switch to Public/i));
  }

  it("toggling a project chip hides that project card", async () => {
    await goPublic();
    // Target the chip button specifically
    fireEvent.click(screen.getByRole("button", { name: /team-project-alpha/i }));
    await waitFor(() => {
      // The card should be gone; the chip (now deselected) still exists in the navbar
      const matches = screen.getAllByText("team-project-alpha");
      expect(matches).toHaveLength(1); // only the chip remains, not the card
      expect(matches[0].closest("button")).toBeInTheDocument(); // it's the chip, not a card
    });
  });

  it("toggling Language Proficiency chip hides the section", async () => {
    await goPublic();
    // Click the chip button specifically, not the section heading <p>
    fireEvent.click(screen.getByRole("button", { name: /Language Proficiency/i }));
    expect(screen.queryByText("JavaScript")).not.toBeInTheDocument();
  });

  it("toggling Growth & Evolution chip hides the section", async () => {
    await renderLoaded({
      ...mockApiResponse,
      portfolio_data: {
        ...mockApiResponse.portfolio_data,
        growth_metrics: {
          has_comparison: false,
          earliest_project: "my-cool-project",
          latest_project: "my-cool-project",
          code_metrics: { commit_growth: 0, file_growth: 0, lines_growth: 0, user_lines_growth: 0 },
          technology_metrics: { framework_growth: 0, earliest_frameworks: 0, latest_frameworks: 0 },
          testing_evolution: { testing_status: "", coverage_improvement: 0, earliest_has_tests: false, latest_has_tests: false },
          collaboration_evolution: { earliest_team_size: 3, latest_team_size: 3, earliest_level: "Top Contributor", latest_level: "Top Contributor", collaboration_summary: "" },
          role_evolution: { earliest_role: "Lead Developer", latest_role: "Lead Developer", role_changed: false },
          framework_timeline_list: [],
        },
      },
    }, "Jane Doe");
    fireEvent.click(screen.getByTitle(/Switch to Public/i));
    fireEvent.click(screen.getByRole("button", { name: /Growth & Evolution/i }));
    // GrowthMetrics section should no longer render
    expect(screen.queryByText(/Moved from a smaller team/i)).not.toBeInTheDocument();
  });
});