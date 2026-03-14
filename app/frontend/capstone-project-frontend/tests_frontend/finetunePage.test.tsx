import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import FinetunePage from "../src/pages/FinetunePage";

const setup = () => {
  const onComplete = vi.fn();
  render(<FinetunePage onComplete={onComplete} />);
  return { onComplete };
};

describe("FinetunePage — initial state", () => {
  it("renders the main heading and section descriptions", () => {
    setup();
    expect(screen.getByText("Fine-tune your analysis")).toBeInTheDocument();
    expect(screen.getByText("Rank & Select Projects")).toBeInTheDocument();
    expect(screen.getByText("Fine-tune Topics")).toBeInTheDocument();
    expect(screen.getByText("Highlight Skills")).toBeInTheDocument();
  });

  it("renders the default projects", () => {
    setup();
    expect(screen.getByText("Capstone Analysis Tool")).toBeInTheDocument();
    expect(screen.getByText("COSC 360 - Android App")).toBeInTheDocument();
    expect(screen.getByText("Personal Portfolio")).toBeInTheDocument();
  });
});

describe("FinetunePage — project selection", () => {
  it("toggles a project selection on click", () => {
    const { onComplete } = setup();
    
    // Click to deselect the first project
    const projectElement = screen.getByText("Capstone Analysis Tool");
    fireEvent.click(projectElement);

    //submit to  internal state changed
    const btn = screen.getByRole("button", { name: /confirm & continue/i });
    fireEvent.click(btn);

    const payload = onComplete.mock.calls[0][0];
    const toggledProject = payload.projects.find((p: any) => p.name === "Capstone Analysis Tool");
    expect(toggledProject.selected).toBe(false);
  });
});

describe("FinetunePage — topics fine-tuning", () => {
  it("removes a keyword when the delete button is clicked", () => {
    setup();
    
    const initialPiggybanks = screen.getAllByText("piggybank");
    expect(initialPiggybanks.length).toBe(2);
    
    // target the first 'piggybank' pill and click its delete button
    const firstPiggybankPill = initialPiggybanks[0];
    const removeBtn = firstPiggybankPill.querySelector("button")!;
    fireEvent.click(removeBtn);

    // Verify only 1 piggybank remains in the DOM
    expect(screen.getAllByText("piggybank").length).toBe(1);
  });

  it("adds a new keyword via input and Enter key", () => {
    setup();
    const inputs = screen.getAllByPlaceholderText("Add keyword...");
    const firstInput = inputs[0];

    fireEvent.change(firstInput, { target: { value: "machine-learning" } });
    fireEvent.keyDown(firstInput, { key: "Enter", code: "Enter" });

    expect(screen.getByText("machine-learning")).toBeInTheDocument();
  });

  it("adds a new topic row", () => {
    setup();
    const addTopicBtn = screen.getByText("+ Add Topic");
    fireEvent.click(addTopicBtn);

    // Verify a new row was added by counting the keyword inputs (starts at 5)
    const inputs = screen.getAllByPlaceholderText("Add keyword...");
    expect(inputs.length).toBe(6);
  });

  it("deletes an entire topic row", () => {
    setup();
    const deleteRowBtns = screen.getAllByTitle("Delete Topic Row");
    fireEvent.click(deleteRowBtns[0]);

    // Verify row was removed (inputs go from 5 down to 4)
    const inputs = screen.getAllByPlaceholderText("Add keyword...");
    expect(inputs.length).toBe(4);
  });
});

describe("FinetunePage — skills highlighting", () => {
  it("enforces a maximum of 3 selected skills", () => {
    setup();

    // Select 3 skills
    fireEvent.click(screen.getByText("PHP"));
    fireEvent.click(screen.getByText("CSS"));
    fireEvent.click(screen.getByText("JavaScript"));

    expect(screen.getByText("Selected (3/3)")).toBeInTheDocument();

    // Verify the 4th skill is disabled
    const fourthSkill = screen.getByText("Web Development");
    expect(fourthSkill).toBeDisabled();
  });

  it("adds a custom skill via input", () => {
    setup();
    const input = screen.getByPlaceholderText("e.g. Docker");
    const addBtn = screen.getByRole("button", { name: "Add Skill" });

    fireEvent.change(input, { target: { value: "Kubernetes" } });
    fireEvent.click(addBtn);

    expect(screen.getByText("Kubernetes")).toBeInTheDocument();
    expect(screen.getByText("Selected (1/3)")).toBeInTheDocument(); // Auto-selects if under 3
  });
});

describe("FinetunePage — submission", () => {
  it("submits the correctly formatted payload on complete", () => {
    const { onComplete } = setup();

    // Select 2 skills
    fireEvent.click(screen.getByText("PHP"));
    fireEvent.click(screen.getByText("CSS"));

    // Click submit
    const btn = screen.getByRole("button", { name: /confirm & continue/i });
    fireEvent.click(btn);

    expect(onComplete).toHaveBeenCalledOnce();

    const payload = onComplete.mock.calls[0][0];

    // Assert Projects structure
    expect(payload.projects).toHaveLength(3);
    expect(payload.projects[0].name).toBe("Capstone Analysis Tool");

    // Assert Topics structure
    expect(payload.topics).toHaveLength(5);
    expect(payload.topics[0].keywords).toContain("user");

    // Assert Skills structure (should only return the 2 selected skills)
    expect(payload.skills).toHaveLength(2);
    expect(payload.skills[0].name).toBe("PH");
    expect(payload.skills[1].name).toBe("CSS");
  });
});

describe("FinetunePage — info modal", () => {
  it("opens and closes the 'What are Topic Vectors?' modal", () => {
    setup();

    // 1. Verify the modal is NOT in the document initially
    expect(screen.queryByText(/Topic vectors are like/i)).not.toBeInTheDocument();

    // 2. Click the trigger link
    const infoLink = screen.getByRole("button", { name: /What are topic vectors\?/i });
    fireEvent.click(infoLink);

    // Verify the modal is now visible
    expect(screen.getByText("What are Topic Vectors?")).toBeInTheDocument();
    expect(screen.getByText(/Topic vectors are like "underlying themes"/i)).toBeInTheDocument();

    // 3. Click the 'Got it' button to close it
    const closeBtn = screen.getByRole("button", { name: /Got it/i });
    fireEvent.click(closeBtn);

    // Verify the modal has been removed from the DOM
    expect(screen.queryByText(/Topic vectors are like/i)).not.toBeInTheDocument();
  });
});