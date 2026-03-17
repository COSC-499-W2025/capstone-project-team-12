import StatCard from "./StatCard";
import SectionCard from "./SectionCard";
import type { Project } from "../types/insightTypes";

interface TestingTabProps {
  p: Project;
}

export default function TestingTab({ p }: TestingTabProps) {
  return (
    <div className="space-y-5">
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <StatCard label="Code Files Modified"  value={p.testing.codeFilesModified} />
        <StatCard label="Code Lines Added"     value={p.testing.codeLinesAdded.toLocaleString()} />
        <StatCard label="Test Files Modified"  value={p.testing.testFilesModified} />
        <StatCard label="Test Lines Added"     value={p.testing.testLinesAdded} />
        <StatCard label="Testing % (files)"    value={`${p.testing.testingPercentageFiles}%`} />
        <StatCard label="Testing % (lines)"    value={`${p.testing.testingPercentageLines}%`} />
      </div>
      <SectionCard title="Test Status" icon="🧪">
        <div className="flex items-center gap-3">
          <span className={`w-3 h-3 rounded-full shrink-0 ${p.testing.hasTests ? "bg-green-500" : "bg-red-400"}`} />
          <span className="text-sm font-semibold text-slate-700">
            {p.testing.hasTests ? "Tests detected in this repo" : "No tests detected in this repo"}
          </span>
        </div>
        {!p.testing.hasTests && (
          <p className="text-xs text-slate-400 mt-2 ml-6">Consider adding unit or integration tests to improve code reliability.</p>
        )}
      </SectionCard>
    </div>
  );
}
