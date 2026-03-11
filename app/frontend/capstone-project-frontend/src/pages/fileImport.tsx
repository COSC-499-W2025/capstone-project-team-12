import React, { useState, useRef, useCallback } from "react";

interface FileImportProps {
  onComplete: () => void;
}

const FileImport: React.FC<FileImportProps> = ({ onComplete }) => {
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback((f: File) => {
    setFile(f);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setIsDragging(false);
      const dropped = e.dataTransfer.files[0];
      if (dropped) handleFile(dropped);
    },
    [handleFile]
  );

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) handleFile(selected);
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const removeFile = () => {
    setFile(null);
    if (inputRef.current) inputRef.current.value = "";
  };

  return (
    <div className="flex-1 min-h-screen bg-[#f8f9fc] flex items-center justify-center font-sans px-6 py-10 relative overflow-hidden">
      {/* Decorative gradient blurs */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 right-[30%] w-[500px] h-[500px] rounded-full bg-[#6378ff] opacity-[0.04] blur-[120px]" />
        <div className="absolute bottom-0 left-[10%] w-[400px] h-[400px] rounded-full bg-[#a78bfa] opacity-[0.03] blur-[100px]" />
      </div>

      <div className="w-full max-w-[480px] relative">
        {/* Header */}
        <div className="mb-9">
          <p className="text-[11px] font-bold tracking-[0.12em] uppercase text-[#6378ff] mb-2.5">
            File Upload
          </p>
          <h1 className="text-[26px] font-extrabold text-[#0f1629] tracking-[-0.02em] leading-tight mb-2">
            Upload your file
          </h1>
          <p className="text-sm text-[#6b7280] leading-relaxed">
            Select or drag a file into the area below, then confirm to continue.
          </p>
        </div>

        {/* Drop zone */}
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => inputRef.current?.click()}
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
              Drag & drop your file here
            </p>
            <p className="text-xs text-[#9ca3af] mt-1">
              or{" "}
              <span className="text-[#6378ff] font-semibold">browse</span>{" "}
              to choose a file
            </p>
          </div>

          <input
            ref={inputRef}
            type="file"
            onChange={handleInputChange}
            className="hidden"
          />
        </div>

        {/* Uploaded file card */}
        {file && (
          <div className="mt-5 flex items-center gap-3 bg-white rounded-xl border border-[rgba(0,0,0,0.06)] px-4 py-3.5 shadow-sm">
            {/* File icon */}
            <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-[#6378ff]/10 flex items-center justify-center">
              <svg
                className="w-5 h-5 text-[#6378ff]"
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
            </div>

            {/* File info */}
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-[#0f1629] truncate">
                {file.name}
              </p>
              <p className="text-xs text-[#9ca3af] mt-0.5">
                {formatSize(file.size)}
              </p>
            </div>

            {/* Remove button */}
            <button
              onClick={removeFile}
              className="flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center text-[#9ca3af] hover:text-red-500 hover:bg-red-50 transition-colors duration-150"
              aria-label="Remove file"
            >
              <svg
                className="w-4 h-4"
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
        )}

        {/* Divider */}
        <div className="h-px bg-black/[0.07] my-6" />

        {/* Confirm button */}
        <button
          onClick={onComplete}
          disabled={!file}
          className={`
            w-full py-3.5 rounded-xl border-none font-bold text-sm
            flex items-center justify-center gap-2
            transition-all duration-200 font-sans
            ${
              file
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
    </div>
  );
};

export default FileImport;
