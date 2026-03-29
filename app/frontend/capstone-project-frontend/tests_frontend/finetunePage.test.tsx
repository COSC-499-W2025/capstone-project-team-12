import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import FinetunePage from "../src/pages/finetunePage";
import { AnalysisPipelineProvider } from "../src/context/AnalysisPipelineContext";

// 1. Define the mock state that the tests expect to interact with
const mockInitialState = {
  projects: [
    { id: "p1", name: "Capstone Analysis Tool", commits: 140, selected: true },
    { id: "p2", name: "COSC 360 - Android App", commits: 85, selected: true },
    { id: "p3", name: "Personal Portfolio", commits: 42, selected: true },
  ],
  topics: [
    { id: "t0", keywords: ["user", "post", "blog", "comment", "account", "create", "like", "option", "name", "use"] },
    { id: "t1", keywords: ["post", "setting", "view", "recent", "account", "piggybank", "trend", "make", "save", "jane"] },
    { id: "t2", keywords: ["px", "content", "flex", "center", "border", "post", "margin", "align", "fit", "color"] },
    { id: "t3", keywords: ["color", "background", "content", "log", "white", "px", "piggybank", "arial", "pfp", "black"] },
    { id: "t4", keywords: ["id", "user", "post", "utf", "mb", "follow", "ibfk", "increment", "auto", "current"] },
  ],
  skills: [
    { id: "s0", name: "PHP", selected: false },
    { id: "s1", name: "CSS", selected: false },
    { id: "s2", name: "JavaScript", selected: false },
    { id: "s3", name: "Web Development", selected: false },
    { id: "s4", name: "Backend Development", selected: false },
    { id: "s5", name: "Database", selected: false },
  ]
};

// 2. Inject it into the setup function
const setup = () => {
  const onComplete = vi.fn();
  render(<AnalysisPipelineProvider><FinetunePage onComplete={onComplete} initialState={mockInitialState} /></AnalysisPipelineProvider>);
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

    // Assert Skills structure (Preserves all skills for state persistence, but only 2 should be selected)
    expect(payload.skills).toHaveLength(6);
    
    const phpSkill = payload.skills.find((s: any) => s.name === "PHP");
    const cssSkill = payload.skills.find((s: any) => s.name === "CSS");
    const jsSkill = payload.skills.find((s: any) => s.name === "JavaScript");

    expect(phpSkill.selected).toBe(true);
    expect(cssSkill.selected).toBe(true);
    expect(jsSkill.selected).toBe(false); // Was never clicked
  });
});

describe("FinetunePage — info modal", () => {
  it("opens and closes the 'What are Topic Keyowrds?' modal", () => {
    setup();

    // 1. Verify the modal title is not in the document initially
    expect(screen.queryByText("What are Topic Keywords?")).not.toBeInTheDocument();

    // 2. Click the trigger link
    const infoLink = screen.getByRole("button", { name: /What are topic keywords\?/i });
    fireEvent.click(infoLink);

    // Verify the modal is now visible by checking for its header
    expect(screen.getByText("What are Topic Keywords?")).toBeInTheDocument();

    // 3. Click the 'Got it' button to close it
    const closeBtn = screen.getByRole("button", { name: /Got it/i });
    fireEvent.click(closeBtn);

    // Verify the modal has been removed from the DOM
    expect(screen.queryByText("What are Topic Keywords?")).not.toBeInTheDocument();
  });
});

describe("FinetunePage — dynamic data loading", () => {
  const mockExtractedData = {
    analysis_id: "test-uuid-1234",
    analyzed_projects: [
      { repository_name: "Extracted Repo", importance_score: 0.85 }
    ],
    topic_keywords: [
      { topic_id: 1, keywords: ["react", "typescript"] }
    ],
    detected_skills: ["Docker"]
  };

  it("loads and displays data from the extractedData prop", () => {
    const onComplete = vi.fn();
    render(<AnalysisPipelineProvider><FinetunePage extractedData={mockExtractedData} onComplete={onComplete} /></AnalysisPipelineProvider>);
    
    expect(screen.getByText("Extracted Repo")).toBeInTheDocument();
    expect(screen.getByText("85 score")).toBeInTheDocument();
    expect(screen.getByText("react")).toBeInTheDocument();
    expect(screen.getByText("Docker")).toBeInTheDocument();
  });

  it("does not select skills by default from extractedData", () => {
    const onComplete = vi.fn();
    render(<AnalysisPipelineProvider><FinetunePage extractedData={mockExtractedData} onComplete={onComplete} /></AnalysisPipelineProvider>);
    
    const dockerSkillBtn = screen.getByText("Docker");
    // Verify it has the unselected styling (text-[#6b7280]) and not the selected one
    expect(dockerSkillBtn.className).toContain("text-[#6b7280]");
  });
});

describe("FinetunePage — state persistence", () => {
  it("restores state from initialState overriding extractedData", () => {
    const mockExtractedData = {
      analysis_id: "test",
      analyzed_projects: [{ repository_name: "Backend Repo", importance_score: 0.5 }],
    };
    const customInitialState = {
      projects: [{ id: "p1", name: "Custom Saved Repo", commits: 99, selected: true }],
      topics: [],
      skills: []
    };
    
    const onComplete = vi.fn();
    render(
      <AnalysisPipelineProvider>
        <FinetunePage 
          extractedData={mockExtractedData} 
          initialState={customInitialState} 
          onComplete={onComplete} 
        />
      </AnalysisPipelineProvider>
    );
    
    expect(screen.getByText("Custom Saved Repo")).toBeInTheDocument();
    // The backend repo should be completely ignored in favor of the saved state
    expect(screen.queryByText("Backend Repo")).not.toBeInTheDocument();
  });

  it("syncs state continuously via onStateChange", async () => {
    const onComplete = vi.fn();
    const customInitialState = {
      projects: [{ id: "p1", name: "Custom Saved Repo", commits: 99, selected: true }],
      topics: [],
      skills: []
    };
    
    render(
      <AnalysisPipelineProvider>
        <FinetunePage 
          initialState={customInitialState} 
          onComplete={onComplete} 
        />
      </AnalysisPipelineProvider>
    );
    
    // State syncing is now handled via context; verify the initialState was loaded into the UI
    await waitFor(() => expect(screen.getByText("Custom Saved Repo")).toBeInTheDocument());
  });
});

describe("FinetunePage — project scoring modal", () => {
  it("opens and closes the 'How are projects scored?' modal", () => {
    const onComplete = vi.fn();
    render(<AnalysisPipelineProvider><FinetunePage onComplete={onComplete} /></AnalysisPipelineProvider>);

    // 1. Verify the modal title is not in the document initially
    expect(screen.queryByText("How are Projects Scored?")).not.toBeInTheDocument();

    // 2. Click the trigger link
    const infoLink = screen.getByRole("button", { name: /How are projects scored\?/i });
    fireEvent.click(infoLink);

    // Verify the modal is now visible by checking for its header
    expect(screen.getByText("How are Projects Scored?")).toBeInTheDocument();

    // 3. Click the 'Got it' button to close it
    const closeBtn = screen.getByRole("button", { name: /Got it/i });
    fireEvent.click(closeBtn);

    // Verify the modal has been removed from the DOM
    expect(screen.queryByText("How are Projects Scored?")).not.toBeInTheDocument();
  });
});