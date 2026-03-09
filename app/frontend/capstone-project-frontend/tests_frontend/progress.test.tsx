import { render, screen, fireEvent, act } from "@testing-library/react";
import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import ProgressPage from "../src/pages/progress";
import React, { useState, useEffect } from "react";

// MOCK TIMERS & RANDOM 
//progress page relies on setInterval and Math.random to simulate progress
//we mock these to fast-forward time and make increments predictable.
beforeEach(() => {
  vi.useFakeTimers();
  // Math.floor(Math.random() * 10) + 5 -> with 0.5, this evaluates to exactly 10.
  vi.spyOn(Math, "random").mockReturnValue(0.5);
});

afterEach(() => {
  vi.restoreAllMocks();
  vi.useRealTimers();
});

// TESTS 

describe("ProgressPage — initial state", () => {
  it("renders the main heading and subtext", () => {
    const mockOnComplete = vi.fn();
    render(<ProgressPage onComplete={mockOnComplete} />);
    
    expect(screen.getByText("Processing Project")).toBeInTheDocument();
    expect(screen.getByText("Please do not close this tab")).toBeInTheDocument();
  });

  it("starts at 0% and displays initialization text", () => {
    const mockOnComplete = vi.fn();
    render(<ProgressPage onComplete={mockOnComplete} />);
    
    expect(screen.getByText("0%")).toBeInTheDocument();
    expect(screen.getByText("Initializing pipeline...")).toBeInTheDocument();
  });

  it("renders a disabled view results button", () => {
    const mockOnComplete = vi.fn();
    render(<ProgressPage onComplete={mockOnComplete} />);
    
    const button = screen.getByRole("button", { name: "View Results" });
    expect(button).toBeDisabled();
  });
});

describe("ProgressPage — progress simulation", () => {
  it("updates progress text and percentage over time", () => {
    const mockOnComplete = vi.fn();
    render(<ProgressPage onComplete={mockOnComplete} />);

    //fast forward 3 intervals (3 * 800ms = 2400ms) -> Progress should jump to 30%
    act(() => {
      vi.advanceTimersByTime(2400);
    });
    expect(screen.getByText("30%")).toBeInTheDocument();
    expect(screen.getByText("Extracting metadata & code...")).toBeInTheDocument();

    //fastforward 3 more intervals to reach 60%
    act(() => {
      vi.advanceTimersByTime(2400);
    });
    expect(screen.getByText("60%")).toBeInTheDocument();
    expect(screen.getByText("Running topic analysis...")).toBeInTheDocument();
  });
});

describe("ProgressPage — completion", () => {
  it("stops at 100% and displays completion text", () => {
    const mockOnComplete = vi.fn();
    render(<ProgressPage onComplete={mockOnComplete} />);

    //fastforward 10 seconds to guarantee it finishes
    act(() => {
      vi.advanceTimersByTime(10000);
    });

    expect(screen.getByText("100%")).toBeInTheDocument();
    expect(screen.getByText("Analysis complete!")).toBeInTheDocument();
    expect(screen.getByText("Ready to view results")).toBeInTheDocument();
  });

  it("enables the button at 100%", () => {
    const mockOnComplete = vi.fn();
    render(<ProgressPage onComplete={mockOnComplete} />);

    act(() => {
      vi.advanceTimersByTime(10000);
    });

    const button = screen.getByRole("button", { name: "View Results" });
    expect(button).not.toBeDisabled();
  });

  it("calls onComplete prop when the active button is clicked", () => {
    const mockOnComplete = vi.fn();
    render(<ProgressPage onComplete={mockOnComplete} />);

    act(() => {
      vi.advanceTimersByTime(10000);
    });

    const button = screen.getByRole("button", { name: "View Results" });
    fireEvent.click(button);

    expect(mockOnComplete).toHaveBeenCalledOnce();
  });
});