import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import "@testing-library/jest-dom";
import { useState } from "react";
import FileImport, { type UploadEntry } from "../src/pages/fileImport";

const setup = () => {
  const onComplete = vi.fn();
  const onUploadsChange = vi.fn();
  render(
    <FileImport
      onComplete={onComplete}
      githubUsername="testuser"
      githubEmail="test@example.com"
      model="test-model"
      uploads={[]}
      onUploadsChange={onUploadsChange}
    />
  );
  return { onComplete, onUploadsChange };
};

/** Wrapper that manages uploads state so the component behaves like it does in the real app */
const StatefulFileImport = ({ onComplete }: { onComplete: () => void }) => {
  const [uploads, setUploads] = useState<UploadEntry[]>([]);
  return (
    <FileImport
      onComplete={onComplete}
      githubUsername="testuser"
      githubEmail="test@example.com"
      model="test-model"
      uploads={uploads}
      onUploadsChange={setUploads}
    />
  );
};

const setupStateful = () => {
  const onComplete = vi.fn();
  render(<StatefulFileImport onComplete={onComplete} />);
  return { onComplete };
};

describe("FileImport", () => {
  const originalFetch = globalThis.fetch;

  beforeEach(() => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      text: () => Promise.resolve(JSON.stringify({ success: true })),
    });
  });

  afterEach(() => {
    globalThis.fetch = originalFetch;
  });

  it("renders heading and description", () => {
    setup();
    expect(screen.getByText("Upload your file or folder")).toBeInTheDocument();
    expect(screen.getByText(/drag a file or folder/i)).toBeInTheDocument();
  });

  it("renders the drop zone with browse prompt", () => {
    setup();
    expect(screen.getByText("Drag & drop files or folders here")).toBeInTheDocument();
    expect(screen.getByText("browse")).toBeInTheDocument();
  });

  it("renders confirm button disabled when no uploads", () => {
    setup();
    const btn = screen.getByRole("button", { name: /confirm & continue/i });
    expect(btn).toBeDisabled();
  });

  it("does not call onComplete when button is disabled", () => {
    const { onComplete } = setup();
    const btn = screen.getByRole("button", { name: /confirm & continue/i });
    fireEvent.click(btn);
    expect(onComplete).not.toHaveBeenCalled();
  });

  it("shows file/folder picker on drop zone click", () => {
    setup();
    const dropZone = screen.getByText("Drag & drop files or folders here").closest("div[class*='border-dashed']")!;
    fireEvent.click(dropZone);
    expect(screen.getByText("Files")).toBeInTheDocument();
    expect(screen.getByText("Folder")).toBeInTheDocument();
    expect(screen.getByText("Select one or more files")).toBeInTheDocument();
    expect(screen.getByText("Select an entire directory")).toBeInTheDocument();
  });

  it("closes picker on outside click", () => {
    setup();
    const dropZone = screen.getByText("Drag & drop files or folders here").closest("div[class*='border-dashed']")!;
    fireEvent.click(dropZone);
    expect(screen.getByText("Files")).toBeInTheDocument();
    fireEvent.mouseDown(document.body);
    expect(screen.queryByText("Select one or more files")).not.toBeInTheDocument();
  });

  it("adds a file via file input and enables confirm button", async () => {
    const { onComplete } = setupStateful();
    const dropZone = screen.getByText("Drag & drop files or folders here").closest("div[class*='border-dashed']")!;
    fireEvent.click(dropZone);

    const fileInput = document.querySelector('input[type="file"]:not([webkitdirectory])') as HTMLInputElement;
    const file = new File(["hello"], "test.txt", { type: "text/plain" });
    Object.defineProperty(fileInput, "files", { value: [file] });
    fireEvent.change(fileInput);

    expect(screen.getByText("test.txt")).toBeInTheDocument();
    expect(screen.getByText("5 B")).toBeInTheDocument();
    expect(screen.getByText("Uploaded Items")).toBeInTheDocument();

    const btn = screen.getByRole("button", { name: /confirm & continue/i });
    expect(btn).not.toBeDisabled();
    fireEvent.click(btn);
    await waitFor(() => expect(onComplete).toHaveBeenCalledOnce());
    expect(globalThis.fetch).toHaveBeenCalledWith(
      "http://localhost:8080/projects/upload/extract",
      expect.objectContaining({ method: "POST" })
    );
  });

  it("removes an uploaded file", () => {
    setupStateful();
    const dropZone = screen.getByText("Drag & drop files or folders here").closest("div[class*='border-dashed']")!;
    fireEvent.click(dropZone);

    const fileInput = document.querySelector('input[type="file"]:not([webkitdirectory])') as HTMLInputElement;
    const file = new File(["data"], "remove-me.txt", { type: "text/plain" });
    Object.defineProperty(fileInput, "files", { value: [file] });
    fireEvent.change(fileInput);

    expect(screen.getByText("remove-me.txt")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /remove upload/i }));
    expect(screen.queryByText("remove-me.txt")).not.toBeInTheDocument();
  });

  it("does not call onComplete when the backend upload fails (e.g. 500 error)", async () => {
    // Suppress console.error for this specific test so the test output stays clean
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    // Mock a backend failure
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
      text: () => Promise.resolve(JSON.stringify({ detail: "Internal Server Error" })),
    });

    const { onComplete } = setupStateful();
    
    // Add a file so the confirm button is enabled
    const dropZone = screen.getByText("Drag & drop files or folders here").closest("div[class*='border-dashed']")!;
    fireEvent.click(dropZone);
    const fileInput = document.querySelector('input[type="file"]:not([webkitdirectory])') as HTMLInputElement;
    const file = new File(["data"], "test.txt", { type: "text/plain" });
    Object.defineProperty(fileInput, "files", { value: [file] });
    fireEvent.change(fileInput);

    // Trigger the upload
    const btn = screen.getByRole("button", { name: /confirm & continue/i });
    fireEvent.click(btn);

    // Wait for the fetch to resolve
    await waitFor(() => {
      expect(globalThis.fetch).toHaveBeenCalled();
    });

    // Ensure the app caught the error and prevented advancement to the next page
    expect(onComplete).not.toHaveBeenCalled();

    consoleSpy.mockRestore();
  });
});