import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, beforeEach, vi } from "vitest";
import "@testing-library/jest-dom";
import CommitHeatmap from "../src/components/CommitHeatmap";

// ─── ResizeObserver mock ───────────────────
beforeEach(() => {
  window.ResizeObserver = class ResizeObserver {
    callback: ResizeObserverCallback;
    constructor(cb: ResizeObserverCallback) { this.callback = cb; }
    observe(el: Element) {
      this.callback([{ contentRect: { width: 800 } } as ResizeObserverEntry], this);
    }
    disconnect() {}
    unobserve() {}
  };
});

// ─── Sample commits ───────────────────────────────────────────────────────────
const makeCommit = (date: string, linesAdded = 10) => ({
  hash: Math.random().toString(36).slice(2),
  date,
  modified_files: [{ filename: "index.ts", change_type: "modified", added_lines: linesAdded, deleted_lines: 0 }],
});

const sampleCommits = [
  makeCommit("2025-02-01T10:00:00-08:00", 20),
  makeCommit("2025-02-01T14:00:00-08:00", 15), // same day, should aggregate
  makeCommit("2025-02-10T09:00:00-08:00", 50),
];

// ─── Tests ────────────────────────────────────────────────────────────────────

describe("CommitHeatmap", () => {

  // Rendering

  it("renders the Commit Activity header by default", () => {
    render(<CommitHeatmap commits={sampleCommits} />);
    expect(screen.getByText("Commit Activity")).toBeInTheDocument();
  });

  it("renders the correct total commit count", () => {
    render(<CommitHeatmap commits={sampleCommits} />);
    expect(screen.getByText(/3 commits/)).toBeInTheDocument();
  });

  it("renders the Commits and Lines Added toggle buttons", () => {
    render(<CommitHeatmap commits={sampleCommits} />);
    expect(screen.getByRole("button", { name: "Commits" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Lines Added" })).toBeInTheDocument();
  });

  it("renders the Less / More legend", () => {
    render(<CommitHeatmap commits={sampleCommits} />);
    expect(screen.getByText("Less")).toBeInTheDocument();
    expect(screen.getByText("More")).toBeInTheDocument();
  });

  it("renders with an empty commits array without crashing", () => {
    render(<CommitHeatmap commits={[]} />);
    expect(screen.getByText("Commit Activity")).toBeInTheDocument();
  });

  // Mode toggle

    it("switches to Lines Added mode when the toggle is clicked", () => {
        render(<CommitHeatmap commits={sampleCommits} />);
        fireEvent.click(screen.getByRole("button", { name: "Lines Added" }));
        const matches = screen.getAllByText("Lines Added");
        expect(matches.some(el => el.tagName === "P")).toBe(true);
    });

  it("shows total lines added after switching to Lines Added mode", () => {
    render(<CommitHeatmap commits={sampleCommits} />);
    fireEvent.click(screen.getByRole("button", { name: "Lines Added" }));
    // 20 + 15 + 50 = 85
    expect(screen.getByText(/85 lines added/)).toBeInTheDocument();
  });

  it("switches back to Commits mode when Commits toggle is clicked", () => {
    render(<CommitHeatmap commits={sampleCommits} />);
    fireEvent.click(screen.getByRole("button", { name: "Lines Added" }));
    fireEvent.click(screen.getByRole("button", { name: "Commits" }));
    expect(screen.getByText("Commit Activity")).toBeInTheDocument();
  });

  // Date range label

  it("displays the project start and end date in the subheading", () => {
    render(<CommitHeatmap commits={sampleCommits} />);
    expect(screen.getByText(/Feb 1, 2025/)).toBeInTheDocument();
    expect(screen.getByText(/Feb 10, 2025/)).toBeInTheDocument();
  });
});