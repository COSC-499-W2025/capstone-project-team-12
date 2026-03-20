import { render, screen, fireEvent, within } from "@testing-library/react";
import { describe, it, expect, afterEach, vi } from "vitest";
import ResumeDisplay, {mockResume} from "../src/pages/resume_display";
import { MemoryRouter } from "react-router-dom";
import '@testing-library/jest-dom';

const setup = () => render(<ResumeDisplay />);

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
    fireEvent.change(screen.getAllByRole("textbox")[0], { target: { value: "Updated summary" } });
    fireEvent.click(screen.getByText("Save"));
    expect(screen.getByText("Updated summary")).toBeInTheDocument();
  });
});

// ─── Education ────────────────────────────────────────────────────────────────

describe("Education & Awards section", () => {
  it("renders default education entry", () => {
    setup();
    const card = getCard("Education");
    expect(within(card).getAllByText(/University of British Columbia/).length).toBeGreaterThan(0);
    expect(within(card).getAllByText(/Bachelor of Science/).length).toBeGreaterThan(0);
  });

  it("adds a new entry", () => {
    setup();
    fireEvent.click(screen.getByText("+ Add Entry"));
    expect(screen.getByPlaceholderText("Institution")).toBeInTheDocument();
  });

  it("removes an entry", () => {
    setup();
    fireEvent.click(within(getCard("Education")).getAllByText("✕")[0]);
    expect(within(getCard("Education")).queryByText(/University of British Columbia/)).not.toBeInTheDocument();
  });

  it("saves edits to an entry", () => {
    setup();
    fireEvent.click(within(getCard("Education")).getByText("Edit"));
    fireEvent.change(screen.getByDisplayValue(/University of British Columbia/), { target: { value: "MIT" } });
    fireEvent.click(screen.getByText("Save"));
    expect(screen.getByText("MIT")).toBeInTheDocument();
  });
});

// ─── Skills ───────────────────────────────────────────────────────────────────

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

// ─── Work Experience ──────────────────────────────────────────────────────────

describe("Work Experience section", () => {
  it("renders default work entry", () => {
    setup();
    const card = getCard("Work Experience");
    expect(within(card).getByText(/UBC Okanagan Computer Science/)).toBeInTheDocument();
    expect(within(card).getByText(/Teaching Assistant/)).toBeInTheDocument();
  });

  it("renders bullet points", () => {
    setup();
    expect(screen.getByText(/Led weekly lab sessions/)).toBeInTheDocument();
  });

  it("shows inputs when Edit is clicked", () => {
    setup();
    fireEvent.click(within(getCard("Work Experience")).getByText("Edit"));
    expect(screen.getByDisplayValue(/UBC Okanagan/)).toBeInTheDocument();
  });

  it("saves edits to an entry", () => {
    setup();
    fireEvent.click(within(getCard("Work Experience")).getByText("Edit"));
    fireEvent.change(screen.getByDisplayValue(/UBC Okanagan Computer Science/), {
      target: { value: "Google" },
    });
    fireEvent.click(within(getCard("Work Experience")).getByText("Save"));
    expect(screen.getByText(/Google/)).toBeInTheDocument();
  });

  it("discards changes on cancel", () => {
    setup();
    fireEvent.click(within(getCard("Work Experience")).getByText("Edit"));
    fireEvent.change(screen.getByDisplayValue(/UBC Okanagan Computer Science/), {
      target: { value: "Google" },
    });
    fireEvent.click(within(getCard("Work Experience")).getByText("Cancel"));
    expect(screen.getByText(/UBC Okanagan Computer Science/)).toBeInTheDocument();
  });

  it("removes an entry", () => {
    setup();
    fireEvent.click(within(getCard("Work Experience")).getByText("✕"));
    expect(within(getCard("Work Experience")).queryByText(/UBC Okanagan/)).not.toBeInTheDocument();
  });

  it("adds a new entry", () => {
    setup();
    fireEvent.click(screen.getByText("+ Add Position"));
    expect(screen.getByPlaceholderText("Company")).toBeInTheDocument();
  });

  it("cancelling a new entry removes it", () => {
    setup();
    const card = getCard("Work Experience");
    const countBefore = within(card).queryAllByText("✕").length;
    fireEvent.click(screen.getByText("+ Add Position"));
    fireEvent.click(screen.getByText("Cancel"));
    expect(within(getCard("Work Experience")).queryAllByText("✕").length).toBe(countBefore);
  });
});

// ─── Awards ───────────────────────────────────────────────────────────────────

describe("Awards section", () => {
  it("renders default award", () => {
    setup();
    const card = getCard("Awards & Honours");
    expect(within(card).getByText("Test Scholars Award")).toBeInTheDocument();
    expect(within(card).getByText(/top 5%/)).toBeInTheDocument();
  });

  it("shows inputs when Edit is clicked", () => {
    setup();
    fireEvent.click(within(getCard("Awards & Honours")).getByText("Edit"));
    expect(screen.getByDisplayValue("Test Scholars Award")).toBeInTheDocument();
  });

  it("saves edits to an entry", () => {
    setup();
    fireEvent.click(within(getCard("Awards & Honours")).getByText("Edit"));
    fireEvent.change(screen.getByDisplayValue("Test Scholars Award"), {
      target: { value: "Dean's Award" },
    });
    fireEvent.click(within(getCard("Awards & Honours")).getByText("Save"));
    expect(screen.getByText("Dean's Award")).toBeInTheDocument();
  });

  it("discards changes on cancel", () => {
    setup();
    fireEvent.click(within(getCard("Awards & Honours")).getByText("Edit"));
    fireEvent.change(screen.getByDisplayValue("Test Scholars Award"), {
      target: { value: "Dean's Award" },
    });
    fireEvent.click(within(getCard("Awards & Honours")).getByText("Cancel"));
    expect(screen.getByText("Test Scholars Award")).toBeInTheDocument();
  });

  it("removes an entry", () => {
    setup();
    fireEvent.click(within(getCard("Awards & Honours")).getByText("✕"));
    expect(within(getCard("Awards & Honours")).queryByText("Test Scholars Award")).not.toBeInTheDocument();
  });

  it("adds a new entry", () => {
    setup();
    fireEvent.click(screen.getByText("+ Add Award"));
    expect(screen.getByPlaceholderText("Award title")).toBeInTheDocument();
  });

  it("cancelling a new award removes it", () => {
    setup();
    const card = getCard("Awards & Honours");
    const countBefore = within(card).queryAllByText("✕").length;
    fireEvent.click(screen.getByText("+ Add Award"));
    fireEvent.click(screen.getByText("Cancel"));
    expect(within(getCard("Awards & Honours")).queryAllByText("✕").length).toBe(countBefore);
  });
});

// ─── Helpers ──────────────────────────────────────────────────────────────────

// setupWithId passes resumeId as a prop — the component no longer reads from useParams
const setupWithId = () =>
  render(
    <MemoryRouter>
      <ResumeDisplay resumeId={1} />
    </MemoryRouter>
  );

const mockGet = () =>
  vi.spyOn(global, "fetch").mockResolvedValueOnce({
    ok: true,
    json: async () => ({ resume_data: mockResume }),
  } as Response);

// ─── Async states (loading / error / saving) ─────────────────────────────────

describe("Async UI states", () => {
  afterEach(() => vi.restoreAllMocks());

  it("shows loading state while fetching", () => {
    vi.spyOn(global, "fetch").mockReturnValue(new Promise(() => {}));
    setupWithId();
    expect(screen.getByText("Loading resume…")).toBeInTheDocument();
  });

  it("shows error when fetch fails", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue({
      ok: false,
      status: 500,
      statusText: "Internal Server Error",
    } as Response);
    setupWithId();
    expect(await screen.findByText(/Error:/)).toBeInTheDocument();
  });

  it("shows saving indicator during PUT", async () => {
    mockGet();
    vi.spyOn(global, "fetch").mockReturnValueOnce(new Promise(() => {})); // PUT hangs

    setupWithId();
    await screen.findByText("yourusername");

    fireEvent.click(within(getCard("Contact")).getByText("Edit"));
    fireEvent.change(screen.getByPlaceholderText("GitHub username"), {
      target: { value: "newuser" },
    });
    fireEvent.click(screen.getByText("Save"));

    expect(await screen.findByText("Saving…")).toBeInTheDocument();
  });

  it("shows error when PUT fails", async () => {
    mockGet();
    vi.spyOn(global, "fetch").mockResolvedValueOnce({
      ok: false,
      status: 500,
      statusText: "Internal Server Error",
    } as Response);

    setupWithId();
    await screen.findByText("yourusername");

    fireEvent.click(within(getCard("Contact")).getByText("Edit"));
    fireEvent.change(screen.getByPlaceholderText("GitHub username"), {
      target: { value: "newuser" },
    });
    fireEvent.click(screen.getByText("Save"));

    expect(await screen.findByText(/Error:/)).toBeInTheDocument();
  });

  it("loads and renders resume from API", async () => {
    mockGet();
    setupWithId();
    expect(await screen.findByText("yourusername")).toBeInTheDocument();
  });
});

// ─── Bullet Editor ────────────────────────────────────────────────────────────

describe("Bullet editor", () => {
  it("adds a bullet in summary", () => {
    setup();
    fireEvent.click(within(getCard("Summary")).getByText("Edit"));
    fireEvent.click(screen.getByText("+ Add bullet"));
    expect(screen.getAllByRole("textbox").length).toBeGreaterThan(2);
  });

  it("removes a bullet in summary", () => {
    setup();
    fireEvent.click(within(getCard("Summary")).getByText("Edit"));
    const countBefore = screen.getAllByRole("textbox").length;
    fireEvent.click(screen.getAllByText("×")[0]);
    expect(screen.getAllByRole("textbox").length).toBe(countBefore - 1);
  });

  it("adds a bullet in work experience", () => {
    setup();
    fireEvent.click(within(getCard("Work Experience")).getByText("Edit"));
    const countBefore = screen.getAllByRole("textbox").length;
    fireEvent.click(screen.getByText("+ Add bullet"));
    expect(screen.getAllByRole("textbox").length).toBe(countBefore + 1);
  });

  it("removes a bullet in work experience", () => {
    setup();
    fireEvent.click(within(getCard("Work Experience")).getByText("Edit"));
    const countBefore = screen.getAllByRole("textbox").length;
    fireEvent.click(screen.getAllByText("×")[0]);
    expect(screen.getAllByRole("textbox").length).toBe(countBefore - 1);
  });
});

// ─── Work entry cancel new ────────────────────────────────────────────────────

describe("Work entry cancel new", () => {
  it("cancelling a new work entry removes the blank card", () => {
    setup();
    const card = getCard("Work Experience");
    fireEvent.click(screen.getByText("+ Add Position"));
    expect(screen.getByPlaceholderText("Company")).toBeInTheDocument();
    fireEvent.click(within(card).getByText("Cancel"));
    expect(screen.queryByPlaceholderText("Company")).not.toBeInTheDocument();
  });

  it("existing entry cancel restores original values", () => {
    setup();
    fireEvent.click(within(getCard("Work Experience")).getByText("Edit"));
    fireEvent.change(screen.getByDisplayValue(/UBC Okanagan Computer Science/), {
      target: { value: "Google" },
    });
    fireEvent.click(within(getCard("Work Experience")).getByText("Cancel"));
    expect(screen.getByText(/UBC Okanagan Computer Science/)).toBeInTheDocument();
  });
});