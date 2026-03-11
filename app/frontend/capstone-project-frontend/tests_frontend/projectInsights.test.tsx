import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import "@testing-library/jest-dom";
import ProjectInsights from "../src/pages/ProjectInsights";


// Mock child tab components
vi.mock("../src/components/OverviewTab",    () => ({ default: ({ p }: any) => <div data-testid="overview-tab">{p.repoName}</div> }));
vi.mock("../src/components/TestingTab",     () => ({ default: ({ p }: any) => <div data-testid="testing-tab">{p.repoName}</div> }));
vi.mock("../src/components/DeploymentTab",  () => ({ default: ({ p }: any) => <div data-testid="deployment-tab">{p.repoName}</div> }));
vi.mock("../src/components/PacingTab",      () => ({ default: ({ p }: any) => <div data-testid="pacing-tab">{p.repoName}</div> }));

describe("ProjectInsights", () => {

  // Rendering

  it("renders the page heading", () => {
    render(<ProjectInsights />);
    expect(screen.getByText("Here are your tailored insights.")).toBeInTheDocument();
  });

    it("renders all project buttons", () => {
        render(<ProjectInsights />);
        expect(screen.getByRole("button", { name: "COSC 360 Project" })).toBeInTheDocument();
        expect(screen.getByRole("button", { name: "Personal Portfolio" })).toBeInTheDocument();
    });


  it("renders all four tab buttons", () => {
    render(<ProjectInsights />);
    ["overview", "testing", "deployment", "pacing & role"].forEach(tab => {
      expect(screen.getByText(tab)).toBeInTheDocument();
    });
  });

  // Default state 

  it("shows the first project selected by default", () => {
    render(<ProjectInsights />);
    expect(screen.getByTestId("overview-tab")).toHaveTextContent("COSC 360 Project");
  });

  it("shows the overview tab by default", () => {
    render(<ProjectInsights />);
    expect(screen.getByTestId("overview-tab")).toBeInTheDocument();
    expect(screen.queryByTestId("testing-tab")).not.toBeInTheDocument();
  });

  // Tab switching 

  it("switches to the testing tab when clicked", () => {
    render(<ProjectInsights />);
    fireEvent.click(screen.getByText("testing"));
    expect(screen.getByTestId("testing-tab")).toBeInTheDocument();
    expect(screen.queryByTestId("overview-tab")).not.toBeInTheDocument();
  });

  it("switches to the deployment tab when clicked", () => {
    render(<ProjectInsights />);
    fireEvent.click(screen.getByText("deployment"));
    expect(screen.getByTestId("deployment-tab")).toBeInTheDocument();
  });

  it("switches to the pacing & role tab when clicked", () => {
    render(<ProjectInsights />);
    fireEvent.click(screen.getByText("pacing & role"));
    expect(screen.getByTestId("pacing-tab")).toBeInTheDocument();
  });

  // Project switching

  it("switches to the second project when its button is clicked", () => {
    render(<ProjectInsights />);
    fireEvent.click(screen.getByText("Personal Portfolio"));
    expect(screen.getByTestId("overview-tab")).toHaveTextContent("Personal Portfolio");
  });

  it("resets to the overview tab when switching projects", () => {
    render(<ProjectInsights />);
    fireEvent.click(screen.getByText("testing"));
    fireEvent.click(screen.getByText("Personal Portfolio"));
    expect(screen.getByTestId("overview-tab")).toBeInTheDocument();
    expect(screen.queryByTestId("testing-tab")).not.toBeInTheDocument();
  });

  // Only one tab visible at a time

  it("only renders one tab content at a time", () => {
    render(<ProjectInsights />);
    fireEvent.click(screen.getByText("deployment"));
    expect(screen.queryByTestId("overview-tab")).not.toBeInTheDocument();
    expect(screen.queryByTestId("testing-tab")).not.toBeInTheDocument();
    expect(screen.queryByTestId("pacing-tab")).not.toBeInTheDocument();
    expect(screen.getByTestId("deployment-tab")).toBeInTheDocument();
  });

  // Passes correct project data to tab 

  it("passes the selected project's data down to the active tab", () => {
    render(<ProjectInsights />);
    fireEvent.click(screen.getByText("Personal Portfolio"));
    fireEvent.click(screen.getByText("testing"));
    expect(screen.getByTestId("testing-tab")).toHaveTextContent("Personal Portfolio");
  });

});