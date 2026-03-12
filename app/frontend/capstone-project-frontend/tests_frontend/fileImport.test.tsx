import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import "@testing-library/jest-dom";
import FileImport from "../src/pages/fileImport";

const setup = () => {
  const onComplete = vi.fn();
  render(
    <FileImport
      onComplete={onComplete}
      githubUsername="testuser"
      githubEmail="test@example.com"
      model="test-model"
    />
  );
  return { onComplete };
};

describe("FileImport", () => {
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

  it("adds a file via file input and enables confirm button", () => {
    const { onComplete } = setup();
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
    expect(onComplete).toHaveBeenCalledOnce();
  });

  it("removes an uploaded file", () => {
    setup();
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

  it("shows re-upload note", () => {
    setup();
    expect(screen.getByText(/you can always come back/i)).toBeInTheDocument();
  });
});
