import SectionCard from "./SectionCard";
import type { FileExtension } from "../insightTypes";

const categoryColors: Record<string, string> = {
  "Documentation":  "bg-sky-100 text-sky-700",
  "Mobile App Dev": "bg-violet-100 text-violet-700",
  "Other":          "bg-slate-100 text-slate-600",
  "Database":       "bg-amber-100 text-amber-700",
  "DevOps":         "bg-green-100 text-green-700",
  "Frontend":       "bg-pink-100 text-pink-700",
  "Styling":        "bg-rose-100 text-rose-700",
};

interface FileExtensionSectionProps {
  fileExtensions: FileExtension[];
}

export default function FileExtensionSection({ fileExtensions }: FileExtensionSectionProps) {
  const maxPct = Math.max(...fileExtensions.map((f) => f.percentage));
  return (
    <SectionCard title="File Extension Statistics" icon="📁">
      <div className="space-y-3">
        {fileExtensions.map((f) => (
          <div key={f.ext} className="flex items-center gap-3">
            <span className="w-12 text-right text-xs font-bold text-slate-500 font-mono shrink-0">{f.ext}</span>
            <div className="flex-1 h-7 bg-slate-100 rounded-lg overflow-hidden relative">
              <div
                className="h-full rounded-lg bg-indigo-200"
                style={{ width: `${(f.percentage / maxPct) * 100}%` }}
              />
              <span className="absolute inset-0 flex items-center px-2.5 text-xs font-semibold text-indigo-800">
                {f.percentage}% · {f.count} file{f.count !== 1 ? "s" : ""}
              </span>
            </div>
            <span className={`shrink-0 text-xs px-2 py-1 rounded-full font-medium ${categoryColors[f.category] ?? "bg-slate-100 text-slate-600"}`}>
              {f.category}
            </span>
          </div>
        ))}
      </div>
    </SectionCard>
  );
}
