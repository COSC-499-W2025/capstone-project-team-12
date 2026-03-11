import React, { useState, useRef, useCallback, useEffect } from "react";
import JSZip from "jszip";

interface UploadEntry {
  name: string;
  isDirectory: boolean;
  files: File[];
  totalSize: number;
}

interface FileImportProps {
  onComplete: () => void;
  githubUsername: string;
  githubEmail: string;
  model: string;
}

/** Recursively read all File objects from a FileSystemDirectoryEntry. */
function readAllEntries(dirEntry: FileSystemDirectoryEntry): Promise<File[]> {
  return new Promise((resolve) => {
    const reader = dirEntry.createReader();
    const allFiles: File[] = [];

    const readBatch = () => {
      reader.readEntries(async (entries) => {
        if (entries.length === 0) {
          resolve(allFiles);
          return;
        }
        for (const entry of entries) {
          if (entry.isFile) {
            const file = await new Promise<File>((res) =>
              (entry as FileSystemFileEntry).file(res)
            );
            allFiles.push(file);
          } else if (entry.isDirectory) {
            const nested = await readAllEntries(entry as FileSystemDirectoryEntry);
            allFiles.push(...nested);
          }
        }
        readBatch(); // keep reading until empty (batched API)
      });
    };
    readBatch();
  });
}

const FileImport: React.FC<FileImportProps> = ({ onComplete, githubUsername, githubEmail, model: _model }) => {
  const [uploads, setUploads] = useState<UploadEntry[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [showPicker, setShowPicker] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const folderInputRef = useRef<HTMLInputElement>(null);
  const pickerRef = useRef<HTMLDivElement>(null);

  // Close picker on outside click
  useEffect(() => {
    if (!showPicker) return;
    const handleClick = (e: MouseEvent) => {
      if (pickerRef.current && !pickerRef.current.contains(e.target as Node)) {
        setShowPicker(false);
      }
    };
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [showPicker]);

  const addUpload = useCallback((name: string, files: File[], isDirectory: boolean) => {
    const totalSize = files.reduce((sum, f) => sum + f.size, 0);
    setUploads((prev) => [...prev, { name, isDirectory, files, totalSize }]);
  }, []);

  const handleDrop = useCallback(
    async (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setIsDragging(false);

      const items = e.dataTransfer.items;
      if (!items || items.length === 0) return;

      const entry = items[0].webkitGetAsEntry?.();
      if (entry?.isDirectory) {
        const files = await readAllEntries(entry as FileSystemDirectoryEntry);
        addUpload(entry.name, files, true);
      } else {
        const dropped = e.dataTransfer.files[0];
        if (dropped) addUpload(dropped.name, [dropped], false);
      }
    },
    [addUpload]
  );

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const fileList = e.target.files;
    if (!fileList || fileList.length === 0) return;
    Array.from(fileList).forEach((f) => addUpload(f.name, [f], false));
    setShowPicker(false);
  };

  const handleFolderInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const fileList = e.target.files;
    if (!fileList || fileList.length === 0) return;
    const firstPath = fileList[0].webkitRelativePath;
    const folderName = firstPath.split("/")[0] || "folder";
    const files = Array.from(fileList);
    addUpload(folderName, files, true);
    setShowPicker(false);
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const removeUpload = (index: number) => {
    setUploads((prev) => prev.filter((_, i) => i !== index));
    if (fileInputRef.current) fileInputRef.current.value = "";
    if (folderInputRef.current) folderInputRef.current.value = "";
  };

  const zipSelectedFiles = async (): Promise<File> => {
    const zip = new JSZip();
    const allFiles = uploads.flatMap((entry) => entry.files);
    for (const file of allFiles) {
      const path = file.webkitRelativePath || file.name;
      zip.file(path, file);
    }
    const blob = await zip.generateAsync({ type: "blob" });
    return new File([blob], "project_files.zip", { type: "application/zip" });
  };

  const handleProcessFiles = async () => {
    try {
      console.log('[UPLOAD] Zipping files...');
      const zipped = await zipSelectedFiles();
      console.log('[UPLOAD] Zip complete, size:', zipped.size, 'bytes');

      const formData = new FormData();
      formData.append('github_username', githubUsername);
      formData.append('github_email', githubEmail);
      formData.append('file', zipped);

      console.log('[UPLOAD] Sending POST /projects/upload/extract ...');
      const fetchStart = performance.now();
      const response = await fetch('/projects/upload/extract', {
        method: 'POST',
        body: formData,
      });
      console.log('[UPLOAD] Response received in', ((performance.now() - fetchStart) / 1000).toFixed(1), 's — status:', response.status);

      const text = await response.text();
      console.log('[UPLOAD] Raw response body:', text.slice(0, 500));

      let data;
      try {
        data = JSON.parse(text);
      } catch (parseErr) {
        console.error('[UPLOAD] JSON parse failed:', parseErr, '— body was:', text.slice(0, 200));
        return;
      }
      console.log('[UPLOAD] Parsed response:', data);

      if (!response.ok) {
        console.error('[UPLOAD] Upload failed:', response.status, data);
        return;
      }

      onComplete();
    } catch (error) {
      console.error('[UPLOAD] Upload error:', error);
    }
  };

  return (
    <div className="flex-1 min-h-screen bg-[#f8f9fc] flex items-center justify-center font-sans px-6 py-10 relative overflow-hidden">
      {/* Decorative gradient blurs */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 right-[30%] w-[500px] h-[500px] rounded-full bg-[#6378ff] opacity-[0.04] blur-[120px]" />
        <div className="absolute bottom-0 left-[10%] w-[400px] h-[400px] rounded-full bg-[#a78bfa] opacity-[0.03] blur-[100px]" />
      </div>

      <div className="w-full max-w-[960px] relative flex gap-8 items-start">
        {/* Left column: header + drop zone + button */}
        <div className="flex-1 min-w-0">
        {/* Header */}
        <div className="mb-9">
          <p className="text-[11px] font-bold tracking-[0.12em] uppercase text-[#6378ff] mb-2.5">
            File Upload
          </p>
          <h1 className="text-[26px] font-extrabold text-[#0f1629] tracking-[-0.02em] leading-tight mb-2">
            Upload your file or folder
          </h1>
          <p className="text-sm text-[#6b7280] leading-relaxed">
            Select or drag a file or folder into the area below, then confirm to continue.
          </p>
        </div>

        {/* Drop zone */}
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => setShowPicker(true)}
          className={`
            relative flex flex-col items-center justify-center gap-3
            w-full min-h-[200px] rounded-xl border-2 border-dashed
            cursor-pointer transition-all duration-200
            ${
              isDragging
                ? "border-[#6378ff] bg-[#6378ff]/[0.04]"
                : "border-[#c4c9d4] bg-[#eef0f6] hover:border-[#a5b4fc] hover:bg-[#f3f4f8]"
            }
          `}
        >
          {/* Upload icon */}
          <svg
            className={`w-10 h-10 transition-colors duration-200 ${
              isDragging ? "text-[#6378ff]" : "text-[#9ca3af]"
            }`}
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="17 8 12 3 7 8" />
            <line x1="12" y1="3" x2="12" y2="15" />
          </svg>

          <div className="text-center">
            <p className="text-sm font-semibold text-[#0f1629]">
              Drag & drop files or folders here
            </p>
            <p className="text-xs text-[#9ca3af] mt-1">
              or click to <span className="text-[#6378ff] font-semibold">browse</span>
            </p>
          </div>

          {/* Picker popover */}
          {showPicker && (
            <div
              ref={pickerRef}
              onClick={(e) => e.stopPropagation()}
              className="absolute z-10 bg-white rounded-xl border border-[rgba(0,0,0,0.08)] shadow-lg p-1.5 flex flex-col gap-1 w-[200px]"
            >
              <button
                type="button"
                onClick={() => { fileInputRef.current?.click(); }}
                className="flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-left text-sm font-semibold text-[#0f1629] hover:bg-[#f3f4f8] transition-colors duration-100 bg-transparent border-none cursor-pointer font-sans w-full"
              >
                <svg className="w-4 h-4 text-[#6378ff] flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                  <polyline points="14 2 14 8 20 8" />
                </svg>
                <div>
                  <span className="block leading-tight">Files</span>
                  <span className="block text-[10px] font-normal text-[#9ca3af] mt-0.5">Select one or more files</span>
                </div>
              </button>
              <button
                type="button"
                onClick={() => { folderInputRef.current?.click(); }}
                className="flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-left text-sm font-semibold text-[#0f1629] hover:bg-[#f3f4f8] transition-colors duration-100 bg-transparent border-none cursor-pointer font-sans w-full"
              >
                <svg className="w-4 h-4 text-[#6378ff] flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
                </svg>
                <div>
                  <span className="block leading-tight">Folder</span>
                  <span className="block text-[10px] font-normal text-[#9ca3af] mt-0.5">Select an entire directory</span>
                </div>
              </button>
            </div>
          )}

          <input
            ref={fileInputRef}
            type="file"
            onChange={handleFileInput}
            multiple
            className="hidden"
          />
          <input
            ref={folderInputRef}
            type="file"
            onChange={handleFolderInput}
            className="hidden"
            {...({ webkitdirectory: "true" } as React.InputHTMLAttributes<HTMLInputElement>)}
          />
        </div>

        {/* Divider */}
        <div className="h-px bg-black/[0.07] my-6" />

        {/* Confirm button */}
        <button
          onClick={handleProcessFiles}
          disabled={uploads.length === 0}
          className={`
            w-full py-3.5 rounded-xl border-none font-bold text-sm
            flex items-center justify-center gap-2
            transition-all duration-200 font-sans
            ${
              uploads.length > 0
                ? "bg-gradient-to-br from-[#6378ff] to-[#a78bfa] text-white shadow-[0_4px_20px_rgba(99,120,255,0.3)] cursor-pointer hover:shadow-[0_6px_28px_rgba(99,120,255,0.4)]"
                : "bg-[#eef0f6] text-[#c4c9d4] cursor-not-allowed"
            }
          `}
        >
          Confirm & Continue
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <line x1="5" y1="12" x2="19" y2="12" />
            <polyline points="12 5 19 12 12 19" />
          </svg>
        </button>

        <p className="text-center text-[11px] text-[#c4c9d4] mt-4">
          You can always come back and re-upload.
        </p>
        </div>

        {/* Right column: uploaded items list */}
        {uploads.length > 0 && (
        <div className="w-[320px] flex-shrink-0 max-h-[calc(100vh-8rem)] flex flex-col">
          <p className="text-[11px] font-bold tracking-[0.1em] uppercase text-[#64748b] mb-3">
            Uploaded Items
          </p>

            <div className="flex flex-col gap-2.5 overflow-y-auto pr-1 min-h-0 max-h-[360px]">
              {uploads.map((entry, idx) => (
                <div
                  key={`${entry.name}-${idx}`}
                  className="flex items-center gap-3 bg-white rounded-xl border border-black/10 px-4 py-3"
                >
                  {/* Icon */}
                  <div className="flex-shrink-0 w-9 h-9 rounded-lg bg-[#6378ff]/10 flex items-center justify-center">
                    {entry.isDirectory ? (
                      <svg
                        className="w-4.5 h-4.5 text-[#6378ff]"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
                      </svg>
                    ) : (
                      <svg
                        className="w-4.5 h-4.5 text-[#6378ff]"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                        <polyline points="14 2 14 8 20 8" />
                      </svg>
                    )}
                  </div>

                  {/* Info */}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-[#0f1629] truncate">
                      {entry.name}
                    </p>
                    <p className="text-xs text-[#9ca3af] mt-0.5">
                      {formatSize(entry.totalSize)}
                      {entry.isDirectory && (
                        <span className="ml-1.5 text-[#64748b]">
                          &middot; {entry.files.length} file{entry.files.length !== 1 && "s"}
                        </span>
                      )}
                    </p>
                  </div>

                  {/* Remove */}
                  <button
                    onClick={() => removeUpload(idx)}
                    className="flex-shrink-0 w-7 h-7 rounded-lg flex items-center justify-center text-[#9ca3af] hover:text-red-500 hover:bg-red-50 transition-colors duration-150"
                    aria-label="Remove upload"
                  >
                    <svg
                      className="w-3.5 h-3.5"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <line x1="18" y1="6" x2="6" y2="18" />
                      <line x1="6" y1="6" x2="18" y2="18" />
                    </svg>
                  </button>
                </div>
              ))}
            </div>
        </div>
        )}
      </div>
    </div>
  );
};

export default FileImport;
