import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import "@testing-library/jest-dom";
import { MemoryRouter } from "react-router-dom";
import ProjectInsights from "../src/pages/ProjectInsights";

// ─── Mock child tab components ────────────────────────────────────────────────
vi.mock("../src/components/OverviewTab",   () => ({ default: ({ p }: any) => <div data-testid="overview-tab">{p.repoName}</div> }));
vi.mock("../src/components/TestingTab",    () => ({ default: ({ p }: any) => <div data-testid="testing-tab">{p.repoName}</div> }));
vi.mock("../src/components/DeploymentTab", () => ({ default: ({ p }: any) => <div data-testid="deployment-tab">{p.repoName}</div> }));
vi.mock("../src/components/PacingTab",     () => ({ default: ({ p }: any) => <div data-testid="pacing-tab">{p.repoName}</div> }));

// ─── Mock API response ────────────────────────────────────────────────────────
// Mirrors the shape mapToProjects() expects from GET /projects
const mockApiProjects = [
  {
    analysis_id: "test-123",
    metadata_insights: null,
    project_insights: {
      analyzed_insights: [
        {
          repository_name: "COSC 360 Project",
          contribution_analysis: { contribution_level: "Top Contributor", rank_by_commits: 1, percentile: 100 },
          repository_context: { all_authors_stats: { user1: {}, user2: {} } },
          collaboration_insights: { is_collaborative: true, user_contribution_share_percentage: 72 },
          testing_insights: { test_files_modified: 2, code_files_modified: 10, testing_percentage_files: 20, test_lines_added: 100, code_lines_added: 500, testing_percentage_lines: 20, has_tests: true },
          success_indicators: {
            deployment: { has_cicd: true, has_containerization: false, cicd_tools: ["GitHub Actions"], containerization_tools: [], hosting_platforms: [] },
            version_control: { avg_lines_per_commit: 25, commit_consistency: "40% end-heavy" },
          },
          statistics: { user_commits: 30 },
          user_role: { role: "Lead Developer", blurb: "Primary contributor." },
          dates: { start_date: "2025-01-01", end_date: "2025-04-01" },
        },
        {
          repository_name: "Personal Portfolio",
          contribution_analysis: { contribution_level: "Sole Contributor", rank_by_commits: 1, percentile: 100 },
          repository_context: { all_authors_stats: { user1: {} } },
          collaboration_insights: { is_collaborative: false, user_contribution_share_percentage: 100 },
          testing_insights: { test_files_modified: 0, code_files_modified: 5, testing_percentage_files: 0, test_lines_added: 0, code_lines_added: 200, testing_percentage_lines: 0, has_tests: false },
          success_indicators: {
            deployment: { has_cicd: false, has_containerization: false, cicd_tools: [], containerization_tools: [], hosting_platforms: [] },
            version_control: { avg_lines_per_commit: 15, commit_consistency: "10% end-heavy" },
          },
          statistics: { user_commits: 12 },
          user_role: { role: "Sole Developer", blurb: "Built solo." },
          dates: { start_date: "2025-02-01", end_date: "2025-03-01" },
        },
      ],
    },
  },
];

// ─── Setup ────────────────────────────────────────────────────────────────────

beforeEach(() => {
  vi.spyOn(globalThis, "fetch").mockResolvedValue({
    ok: true,
    json: async () => mockApiProjects,
  } as Response);
});

afterEach(() => {
  vi.restoreAllMocks();
});

async function renderLoaded() {
  render(<MemoryRouter><ProjectInsights analysisId="test-123" /></MemoryRouter>);
  // Wait for the tab content to appear, not the selector button (same text, two elements)
  await screen.findByTestId("overview-tab");
}

// ─── Tests ────────────────────────────────────────────────────────────────────

describe("ProjectInsights", () => {

  // Rendering

  it("renders the page heading", async () => {
    await renderLoaded();
    expect(screen.getByText("Here are your tailored insights.")).toBeInTheDocument();
  });

  it("renders all project buttons", async () => {
    await renderLoaded();
    expect(screen.getByRole("button", { name: "COSC 360 Project" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Personal Portfolio" })).toBeInTheDocument();
  });

  it("renders all four tab buttons", async () => {
    await renderLoaded();
    ["overview", "testing", "deployment", "pacing & role"].forEach(tab => {
      expect(screen.getByText(tab)).toBeInTheDocument();
    });
  });

  // Default state

  it("shows the first project selected by default", async () => {
    await renderLoaded();
    expect(screen.getByTestId("overview-tab")).toHaveTextContent("COSC 360 Project");
  });

  it("shows the overview tab by default", async () => {
    await renderLoaded();
    expect(screen.getByTestId("overview-tab")).toBeInTheDocument();
    expect(screen.queryByTestId("testing-tab")).not.toBeInTheDocument();
  });

  // Tab switching

  it("switches to the testing tab when clicked", async () => {
    await renderLoaded();
    fireEvent.click(screen.getByText("testing"));
    expect(screen.getByTestId("testing-tab")).toBeInTheDocument();
    expect(screen.queryByTestId("overview-tab")).not.toBeInTheDocument();
  });

  it("switches to the deployment tab when clicked", async () => {
    await renderLoaded();
    fireEvent.click(screen.getByText("deployment"));
    expect(screen.getByTestId("deployment-tab")).toBeInTheDocument();
  });

  it("switches to the pacing & role tab when clicked", async () => {
    await renderLoaded();
    fireEvent.click(screen.getByText("pacing & role"));
    expect(screen.getByTestId("pacing-tab")).toBeInTheDocument();
  });

  // Project switching

  it("switches to the second project when its button is clicked", async () => {
    await renderLoaded();
    fireEvent.click(screen.getByRole("button", { name: "Personal Portfolio" }));
    expect(screen.getByTestId("overview-tab")).toHaveTextContent("Personal Portfolio");
  });

  it("resets to the overview tab when switching projects", async () => {
    await renderLoaded();
    fireEvent.click(screen.getByText("testing"));
    fireEvent.click(screen.getByRole("button", { name: "Personal Portfolio" }));
    expect(screen.getByTestId("overview-tab")).toBeInTheDocument();
    expect(screen.queryByTestId("testing-tab")).not.toBeInTheDocument();
  });

  // Only one tab visible at a time

  it("only renders one tab content at a time", async () => {
    await renderLoaded();
    fireEvent.click(screen.getByText("deployment"));
    expect(screen.queryByTestId("overview-tab")).not.toBeInTheDocument();
    expect(screen.queryByTestId("testing-tab")).not.toBeInTheDocument();
    expect(screen.queryByTestId("pacing-tab")).not.toBeInTheDocument();
    expect(screen.getByTestId("deployment-tab")).toBeInTheDocument();
  });

  // Passes correct project data to tab

  it("passes the selected project's data down to the active tab", async () => {
    await renderLoaded();
    fireEvent.click(screen.getByRole("button", { name: "Personal Portfolio" }));
    fireEvent.click(screen.getByText("testing"));
    expect(screen.getByTestId("testing-tab")).toHaveTextContent("Personal Portfolio");
  });

});