import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, waitFor, within } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import Dashboard, { EmptyState } from "../src/pages/dashboard";

const mockProjects = [
  {
    analysis_id: "a1b2c3",
    analysis_title: "Spring 2025 Analyses",
    creation_date: "2025-03-01T00:00:00Z",
    metadata_insights: null,
    project_insights: JSON.stringify({ analyzed_insights: [{ repository_name: "repo-a" }] }),
    file_path: "",
  },
  {
    analysis_id: "d4e5f6",
    analysis_title: "Winter 2025 Analyses",
    creation_date: "2025-01-15T00:00:00Z",
    metadata_insights: null,
    project_insights: JSON.stringify({ analyzed_insights: [{ repository_name: "repo-b" }] }),
    file_path: "",
  },
  {
    analysis_id: "g7h8i9",
    analysis_title: "Fall 2024 Analyses",
    creation_date: "2024-10-12T00:00:00Z",
    metadata_insights: null,
    project_insights: JSON.stringify({ analyzed_insights: [{ repository_name: "repo-c" }] }),
    file_path: "",
  },
];

const mockResumes = [
  { resume_id: 101, analysis_id: "a1b2c3", resume_title: null, resume_data: {} },
  { resume_id: 102, analysis_id: "d4e5f6", resume_title: null, resume_data: {} },
];

const mockPortfolios = [
  { portfolio_id: 201, analysis_id: "a1b2c3", portfolio_title: null, portfolio_data: {} },
];

function jsonResponse(data: unknown, ok = true): Response {
  return {
    ok,
    json: async () => data,
  } as Response;
}

beforeEach(() => {
  vi.spyOn(globalThis, "fetch").mockImplementation((input: RequestInfo | URL, init?: RequestInit) => {
    const url = typeof input === "string" ? input : input.toString();
    const method = init?.method ?? "GET";

    if (method === "GET" && url.endsWith("/projects")) return Promise.resolve(jsonResponse(mockProjects));
    if (method === "GET" && url.endsWith("/resumes")) return Promise.resolve(jsonResponse(mockResumes));
    if (method === "GET" && url.endsWith("/portfolios")) return Promise.resolve(jsonResponse(mockPortfolios));

    if (method === "DELETE" && (url.includes("/projects/") || url.includes("/resume/") || url.includes("/portfolio/"))) {
      return Promise.resolve(jsonResponse({}));
    }

    return Promise.resolve(jsonResponse({}, false));
  });
});

afterEach(() => {
  vi.restoreAllMocks();
});

// ─── Mocks ────────────────────────────────────────────────────────────────────

vi.mock("../src/components/modals", () => ({
  NewAnalysisModal: ({ onConfirm, onCancel }: {
    onConfirm: (p: { label: string; repos: string[] }) => void;
    onCancel: () => void;
  }) => (
    <div data-testid="new-analysis-modal">
      <button onClick={() => onConfirm({ label: "Test Analysis", repos: ["github.com/test/repo"] })}>
        Confirm
      </button>
      <button onClick={onCancel}>Cancel</button>
    </div>
  ),
}));

vi.mock("../src/components/analysisCard", () => ({
  AnalysisCard: ({ analysis, onDelete, onDeleteResume, onDeletePortfolio, onIncremental, onViewResume, onViewPortfolio, onViewInsights }: any) => (
    <div data-testid={`analysis-card-${analysis.id}`}>
      <span>{analysis.label}</span>
      <button onClick={() => onDelete(analysis.id)}>Delete</button>
      <button onClick={() => onDeleteResume(analysis.resumeIds[0])}>Delete Resume</button>
      <button onClick={() => onDeletePortfolio(analysis.portfolioIds[0])}>Delete Portfolio</button>
      <button onClick={() => onIncremental(analysis.id, ["file1"])}>Incremental</button>
      <button onClick={() => onViewResume(analysis, analysis.resumeIds[0])}>View Resume</button>
      <button onClick={() => onViewPortfolio(analysis, analysis.portfolioIds[0])}>View Portfolio</button>
      <button onClick={() => onViewInsights(analysis)}>View Insights</button>
    </div>
  ),
}));

// ─── Helpers ──────────────────────────────────────────────────────────────────

function renderDashboard() {
  return render(
    <MemoryRouter>
      <Dashboard />
    </MemoryRouter>
  );
}

async function renderLoadedDashboard() {
  renderDashboard();
  await screen.findByTestId("analysis-card-a1b2c3");
}

// ─── EmptyState ───────────────────────────────────────────────────────────────

describe("EmptyState", () => {
  it("renders the empty state message", () => {
    render(<EmptyState onNew={() => {}} />);
    expect(screen.getByText("No analyses yet")).toBeInTheDocument();
    expect(screen.getByText(/Run your first analysis/i)).toBeInTheDocument();
  });

  it("calls onNew when the button is clicked", () => {
    const onNew = vi.fn();
    render(<EmptyState onNew={onNew} />);
    fireEvent.click(screen.getByRole("button", { name: /new analysis/i }));
    expect(onNew).toHaveBeenCalledOnce();
  });
});

// ─── Dashboard header ─────────────────────────────────────────────────────────

describe("Dashboard header", () => {
  it("renders the page title and subtitle", () => {
    renderDashboard();
    expect(screen.getByText("Your analyses.")).toBeInTheDocument();
    expect(screen.getByText(/Manage past analyses/i)).toBeInTheDocument();
  });

  it("renders the New Analysis button", () => {
    renderDashboard();
    expect(screen.getByRole("button", { name: /new analysis/i })).toBeInTheDocument();
  });
});

// ─── Stats strip ─────────────────────────────────────────────────────────────

describe("Stats strip", () => {
  it("shows the correct analyses count", async () => {
    await renderLoadedDashboard();
    // 3 mock analyses in the default data
    expect(screen.getByText("3")).toBeInTheDocument();
  });

  it("shows the correct resume count", async () => {
    await renderLoadedDashboard();
    // 2 of 3 mock analyses have hasResume: true
    const resumeCard = screen.getByText("Resumes").closest("div")!;
    expect(within(resumeCard).getByText("2")).toBeInTheDocument();
  });

  it("shows the correct portfolio count", async () => {
    await renderLoadedDashboard();
    // 1 of 3 mock analyses has hasPortfolio: true
    const portfolioCard = screen.getByText("Portfolios").closest("div")!;
    expect(within(portfolioCard).getByText("1")).toBeInTheDocument();
  });
});

// ─── Analysis cards ───────────────────────────────────────────────────────────

describe("Analysis cards", () => {
  it("renders a card for each mock analysis", async () => {
    await renderLoadedDashboard();
    expect(screen.getByTestId("analysis-card-a1b2c3")).toBeInTheDocument();
    expect(screen.getByTestId("analysis-card-d4e5f6")).toBeInTheDocument();
    expect(screen.getByTestId("analysis-card-g7h8i9")).toBeInTheDocument();
  });

  it("renders analysis labels", async () => {
    await renderLoadedDashboard();
    expect(screen.getByText("Spring 2025 Analyses")).toBeInTheDocument();
    expect(screen.getByText("Winter 2025 Analyses")).toBeInTheDocument();
    expect(screen.getByText("Fall 2024 Analyses")).toBeInTheDocument();
  });
});

// ─── Delete analysis ──────────────────────────────────────────────────────────

describe("Deleting an analysis", () => {
  it("removes the card from the list", async () => {
    await renderLoadedDashboard();
    const card = screen.getByTestId("analysis-card-a1b2c3");
    fireEvent.click(within(card).getByRole("button", { name: /^delete$/i }));
    await waitFor(() => {
      expect(screen.queryByTestId("analysis-card-a1b2c3")).not.toBeInTheDocument();
    });
  });

  it("shows a toast after deletion", async () => {
    await renderLoadedDashboard();
    const card = screen.getByTestId("analysis-card-a1b2c3");
    fireEvent.click(within(card).getByRole("button", { name: /^delete$/i }));
    await waitFor(() => {
      expect(screen.getByText("Analysis deleted.")).toBeInTheDocument();
    });
  });

  it("decrements the analyses count in the stats strip", async () => {
    await renderLoadedDashboard();
    const card = screen.getByTestId("analysis-card-a1b2c3");
    fireEvent.click(within(card).getByRole("button", { name: /^delete$/i }));
    await waitFor(() => {
      expect(screen.getByText("2")).toBeInTheDocument();
    });
  });

  it("shows the empty state when all analyses are deleted", async () => {
    await renderLoadedDashboard();
    for (const id of ["a1b2c3", "d4e5f6", "g7h8i9"]) {
      const card = screen.getByTestId(`analysis-card-${id}`);
      fireEvent.click(within(card).getByRole("button", { name: /^delete$/i }));
    }
    await waitFor(() => {
      expect(screen.getByText("No analyses yet")).toBeInTheDocument();
    });
  });
});

// ─── Delete resume ────────────────────────────────────────────────────────────

describe("Deleting a resume", () => {
  it("shows a toast", async () => {
    await renderLoadedDashboard();
    const card = screen.getByTestId("analysis-card-a1b2c3");
    fireEvent.click(within(card).getByRole("button", { name: /delete resume/i }));
    await waitFor(() => {
      expect(screen.getByText("Resume deleted.")).toBeInTheDocument();
    });
  });

  it("decrements the resume count in the stats strip", async () => {
    await renderLoadedDashboard();
    const card = screen.getByTestId("analysis-card-a1b2c3");
    fireEvent.click(within(card).getByRole("button", { name: /delete resume/i }));
    await waitFor(() => {
      const resumeCard = screen.getByText("Resumes").closest("div")!;
      expect(within(resumeCard).getByText("1")).toBeInTheDocument();
    });
  });
});

// ─── Delete portfolio ─────────────────────────────────────────────────────────

describe("Deleting a portfolio", () => {
  it("shows a toast", async () => {
    await renderLoadedDashboard();
    const card = screen.getByTestId("analysis-card-a1b2c3");
    fireEvent.click(within(card).getByRole("button", { name: /delete portfolio/i }));
    await waitFor(() => {
      expect(screen.getByText("Portfolio deleted.")).toBeInTheDocument();
    });
  });

  it("decrements the portfolio count in the stats strip", async () => {
    await renderLoadedDashboard();
    const card = screen.getByTestId("analysis-card-a1b2c3");
    fireEvent.click(within(card).getByRole("button", { name: /delete portfolio/i }));
    await waitFor(() => {
      const portfolioCard = screen.getByText("Portfolios").closest("div")!;
      expect(within(portfolioCard).getByText("0")).toBeInTheDocument();
    });
  });
});


// ─── New Analysis modal ───────────────────────────────────────────────────────

describe("New Analysis modal", () => {
  it("opens when the New Analysis button is clicked", () => {
    renderDashboard();
    fireEvent.click(screen.getByRole("button", { name: /new analysis/i }));
    expect(screen.getByTestId("new-analysis-modal")).toBeInTheDocument();
  });

  it("closes when cancelled", async () => {
    renderDashboard();
    fireEvent.click(screen.getByRole("button", { name: /new analysis/i }));
    fireEvent.click(screen.getByRole("button", { name: /cancel/i }));
    await waitFor(() => {
      expect(screen.queryByTestId("new-analysis-modal")).not.toBeInTheDocument();
    });
  });

  it("adds a new card and closes modal on confirm", async () => {
    await renderLoadedDashboard();
    fireEvent.click(screen.getByRole("button", { name: /new analysis/i }));
    fireEvent.click(screen.getByRole("button", { name: /confirm/i }));
    await waitFor(() => {
      expect(screen.queryByTestId("new-analysis-modal")).not.toBeInTheDocument();
      expect(screen.getByText("Test Analysis")).toBeInTheDocument();
    });
  });

  it("increments the analyses count after adding", async () => {
    await renderLoadedDashboard();
    fireEvent.click(screen.getByRole("button", { name: /new analysis/i }));
    fireEvent.click(screen.getByRole("button", { name: /confirm/i }));
    await waitFor(() => {
      expect(screen.getByText("4")).toBeInTheDocument();
    });
  });

  it("shows a toast after adding", async () => {
    await renderLoadedDashboard();
    fireEvent.click(screen.getByRole("button", { name: /new analysis/i }));
    fireEvent.click(screen.getByRole("button", { name: /confirm/i }));
    await waitFor(() => {
      expect(screen.getByText(/Analysis created/i)).toBeInTheDocument();
    });
  });
});

// ─── Toast auto-dismiss ───────────────────────────────────────────────────────

  it("can be manually dismissed", async () => {
    await renderLoadedDashboard();
    const card = screen.getByTestId("analysis-card-a1b2c3");
    fireEvent.click(within(card).getByRole("button", { name: /^delete$/i }));
    const toast = (await screen.findByText("Analysis deleted.")).closest("div")!;
    fireEvent.click(within(toast).getByRole("button"));
    await waitFor(() => {
      expect(screen.queryByText("Analysis deleted.")).not.toBeInTheDocument();
    });
  });
