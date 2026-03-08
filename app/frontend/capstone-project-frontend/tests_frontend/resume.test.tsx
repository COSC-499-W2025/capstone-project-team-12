import { render, screen, fireEvent, within } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import ResumeDisplay from "../src/pages/resume_display";

const setup = () => render(<ResumeDisplay />);

// SectionCard renders a rounded-2xl card — scope queries to the whole card
// so Edit/Save/Cancel buttons are reachable from within the right section.
const getCard = (title: string) =>
  screen.getByText(title).closest(".rounded-2xl") as HTMLElement;

// ─── Contact ──────────────────────────────────────────────────────────────────

describe("Contact section", () => {
  it("renders github username and email", () => {
    setup();
    expect(screen.getByText("yourusername")).toBeInTheDocument();
    expect(screen.getByText("you@example.com")).toBeInTheDocument();
  });

  it("shows inputs when Edit is clicked", () => {
    setup();
    fireEvent.click(within(getCard("Contact")).getByText("Edit"));
    expect(screen.getByPlaceholderText("GitHub username")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Email address")).toBeInTheDocument();
  });

  it("saves updated values", () => {
    setup();
    fireEvent.click(within(getCard("Contact")).getByText("Edit"));
    fireEvent.change(screen.getByPlaceholderText("GitHub username"), { target: { value: "newuser" } });
    fireEvent.click(screen.getByText("Save"));
    expect(screen.getByText("newuser")).toBeInTheDocument();
  });

  it("discards changes on cancel", () => {
    setup();
    fireEvent.click(within(getCard("Contact")).getByText("Edit"));
    fireEvent.change(screen.getByPlaceholderText("GitHub username"), { target: { value: "newuser" } });
    fireEvent.click(screen.getByText("Cancel"));
    expect(screen.getByText("yourusername")).toBeInTheDocument();
  });
});

// ─── Summary ──────────────────────────────────────────────────────────────────

describe("Summary section", () => {
  it("renders summary text", () => {
    setup();
    expect(screen.getByText(/Full-stack developer/)).toBeInTheDocument();
  });

  it("saves updated summary", () => {
    setup();
    fireEvent.click(within(getCard("Summary")).getByText("Edit"));
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "Updated summary" } });
    fireEvent.click(screen.getByText("Save"));
    expect(screen.getByText("Updated summary")).toBeInTheDocument();
  });
});

// ─── Education ────────────────────────────────────────────────────────────────

describe("Education & Awards section", () => {
  it("renders default education entry", () => {
    setup();
    expect(screen.getByText(/University of British Columbia/)).toBeInTheDocument();
    expect(screen.getByText(/Bachelor of Science/)).toBeInTheDocument();
  });

  it("adds a new entry", () => {
    setup();
    fireEvent.click(screen.getByText("+ Add Entry"));
    expect(screen.getByDisplayValue("Institution Name")).toBeInTheDocument();
  });

  it("removes an entry", () => {
    setup();
    fireEvent.click(screen.getByText("✕"));
    expect(screen.queryByText(/University of British Columbia/)).not.toBeInTheDocument();
  });

  it("saves edits to an entry", () => {
    setup();
    fireEvent.click(within(getCard("Education & Awards")).getByText("Edit"));
    fireEvent.change(screen.getByDisplayValue(/University of British Columbia/), { target: { value: "MIT" } });
    fireEvent.click(screen.getByText("Save"));
    expect(screen.getByText("MIT")).toBeInTheDocument();
  });
});

// ─── Skills ───────────────────────────────────────────────────────────────────
// Note: Skills and Projects share framework names (TypeScript, Docker, React etc.)
// so all skill text queries use getAllByText and are scoped to the Skills card.

describe("Skills section", () => {
  it("renders detected skills", () => {
    setup();
    const card = getCard("Skills");
    expect(within(card).getAllByText("TypeScript").length).toBeGreaterThan(0);
    expect(within(card).getAllByText("React").length).toBeGreaterThan(0);
    expect(within(card).getAllByText("Docker").length).toBeGreaterThan(0);
  });

  it("removes a skill in edit mode", () => {
    setup();
    const card = getCard("Skills");
    fireEvent.click(within(card).getByText("Edit"));
    // scope to the Skills card to avoid matching the TypeScript chip in frameworks
    const chip = within(card).getAllByText("TypeScript")[0].closest("span")!;
    fireEvent.click(within(chip).getByText("×"));
    fireEvent.click(screen.getByText("Save"));
    expect(within(getCard("Skills")).queryByText("TypeScript")).not.toBeInTheDocument();
  });

  it("adds a new skill", () => {
    setup();
    fireEvent.click(within(getCard("Skills")).getByText("Edit"));
    fireEvent.change(screen.getByPlaceholderText("Add skill…"), { target: { value: "Rust" } });
    fireEvent.click(screen.getAllByText("+ Add")[0]);
    fireEvent.click(screen.getByText("Save"));
    expect(within(getCard("Skills")).getByText("Rust")).toBeInTheDocument();
  });

  it("does not add duplicate skills", () => {
    setup();
    const card = getCard("Skills");
    const countBefore = within(card).getAllByText("React").length;
    fireEvent.click(within(card).getByText("Edit"));
    fireEvent.change(screen.getByPlaceholderText("Add skill…"), { target: { value: "React" } });
    fireEvent.click(screen.getAllByText("+ Add")[0]);
    // count within the Skills card should not have increased
    expect(within(getCard("Skills")).getAllByText("React").length).toBe(countBefore);
  });
});

// ─── Projects ─────────────────────────────────────────────────────────────────

describe("Projects section", () => {
  it("renders all project names", () => {
    setup();
    expect(screen.getByText("Capstone Analysis Tool")).toBeInTheDocument();
    expect(screen.getByText("COSC 360 – Android App")).toBeInTheDocument();
    expect(screen.getByText("Personal Portfolio")).toBeInTheDocument();
  });

  it("renders date ranges", () => {
    setup();
    expect(screen.getByText("Jan 2025 - Apr 2025")).toBeInTheDocument();
  });

  it("renders framework chips", () => {
    setup();
    expect(screen.getByText("FastAPI")).toBeInTheDocument();
    expect(screen.getAllByText("PostgreSQL").length).toBeGreaterThan(0);
  });

  it("renders insight bullet", () => {
    setup();
    expect(screen.getByText(/substantial amount of new code/)).toBeInTheDocument();
  });

  it("saves edited project name", () => {
    setup();
    const card = screen.getByText("Capstone Analysis Tool").closest(".rounded-xl") as HTMLElement;
    fireEvent.click(within(card).getByText("Edit"));
    fireEvent.change(screen.getByDisplayValue("Capstone Analysis Tool"), { target: { value: "Updated Project" } });
    fireEvent.click(within(card).getByText("Save"));
    expect(screen.getByText("Updated Project")).toBeInTheDocument();
  });
});

// ─── Languages ────────────────────────────────────────────────────────────────
// Note: language names overlap with Skills (TypeScript, Python) and project
// frameworks (XML) so all queries are scoped to the Languages card.

describe("Languages section", () => {
  it("renders all language names", () => {
    setup();
    const card = getCard("Programming Languages");
    expect(within(card).getAllByText("TypeScript").length).toBeGreaterThan(0);
    expect(within(card).getAllByText("Python").length).toBeGreaterThan(0);
    expect(within(card).getAllByText("XML").length).toBeGreaterThan(0);
  });

  it("renders file counts", () => {
    setup();
    expect(screen.getByText("18 files")).toBeInTheDocument();
    expect(screen.getByText("50 files")).toBeInTheDocument();
  });

  it("adds a new language", () => {
    setup();
    fireEvent.click(within(getCard("Programming Languages")).getByText("Edit"));
    fireEvent.change(screen.getByPlaceholderText("Add language…"), { target: { value: "Rust" } });
    fireEvent.click(screen.getAllByText("+ Add")[0]);
    fireEvent.click(screen.getByText("Save"));
    expect(within(getCard("Programming Languages")).getByText("Rust")).toBeInTheDocument();
  });

  it("removes a language in edit mode", () => {
    setup();
    const card = getCard("Programming Languages");
    fireEvent.click(within(card).getByText("Edit"));
    fireEvent.click(within(card).getAllByText("×")[0]);
    fireEvent.click(screen.getByText("Save"));
    expect(within(getCard("Programming Languages")).queryByText("TypeScript")).not.toBeInTheDocument();
  });
});

// ─── Download button ──────────────────────────────────────────────────────────

describe("Download button", () => {
  it("renders as disabled", () => {
    setup();
    expect(screen.getByText("Download Resume").closest("button")).toBeDisabled();
  });

  it("renders the Soon badge", () => {
    setup();
    expect(screen.getByText("Soon")).toBeInTheDocument();
  });
});