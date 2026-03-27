import { useState, useMemo } from "react";

type Commit = {
  hash: string;
  date: string;
  modified_files: {
    filename: string;
    change_type: string;
    added_lines: number;
    deleted_lines: number;
  }[];
};

type HeatmapMode = "commits" | "lines";

interface CommitHeatmapProps {
  commits: Commit[];
}

function getWeekStart(date: Date): Date {
  const d = new Date(date);
  d.setHours(0, 0, 0, 0);
  d.setDate(d.getDate() - d.getDay()); // Sunday
  return d;
}

// Always use local year/month/day so grid keys and commit keys are in the same space
function toLocalDateKey(date: Date): string {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

// Slice the date portion directly from the ISO string — this is already local time
// e.g. "2025-02-26T16:24:06-08:00" → "2025-02-26"
function isoToLocalKey(iso: string): string {
  return iso.slice(0, 10);
}

// Each cell is w-3 (12px) + gap-1 (4px) = 16px per column
const COL_WIDTH = 16;

export default function CommitHeatmap({ commits }: CommitHeatmapProps) {
  const [mode, setMode] = useState<HeatmapMode>("commits");
  const [tooltip, setTooltip] = useState<{
    x: number;
    y: number;
    date: string;
    value: number;
  } | null>(null);

  // Build a map of date -> { commits, lines } using the local date from the ISO string
  const dailyData = useMemo(() => {
    const map: Record<string, { commits: number; lines: number }> = {};
    for (const commit of commits) {
      const key = isoToLocalKey(commit.date);
      if (!map[key]) map[key] = { commits: 0, lines: 0 };
      map[key].commits += 1;
      map[key].lines += commit.modified_files.reduce(
        (sum, f) => sum + (f.added_lines ?? 0),
        0
      );
    }
    return map;
  }, [commits]);

  // Derive project date range directly from commits
  const { projectStart, projectEnd, startLabel, endLabel } = useMemo(() => {
    if (commits.length === 0) {
      const today = new Date();
      return { projectStart: today, projectEnd: today, startLabel: "", endLabel: "" };
    }
    const dates = commits.map((c) => new Date(c.date).getTime());
    const earliest = new Date(Math.min(...dates));
    const latest = new Date(Math.max(...dates));
    const fmt = (d: Date) => d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
    return { projectStart: earliest, projectEnd: latest, startLabel: fmt(earliest), endLabel: fmt(latest) };
  }, [commits]);

  // Build grid spanning the project timeline
  const { weeks, months } = useMemo(() => {
    const gridStart = getWeekStart(projectStart);
    const daysUntilSat = (6 - projectEnd.getDay() + 7) % 7;
    const gridEnd = new Date(projectEnd);
    gridEnd.setDate(gridEnd.getDate() + daysUntilSat);

    const MIN_WEEKS = 26;
    const naturalWeeks = Math.ceil((Math.round((gridEnd.getTime() - gridStart.getTime()) / 86400000) + 1) / 7);
    const totalWeeks = Math.max(naturalWeeks, MIN_WEEKS);
    if (totalWeeks > naturalWeeks) {
      gridStart.setDate(gridStart.getDate() - (totalWeeks - naturalWeeks) * 7);
    }

    const weeksArr: { date: Date; key: string }[][] = [];
    const monthLabels: { label: string; col: number }[] = [];

    let cursor = new Date(gridStart);
    let lastMonth = -1;

    for (let w = 0; w < totalWeeks; w++) {
      const week: { date: Date; key: string }[] = [];
      for (let d = 0; d < 7; d++) {
        const day = new Date(cursor);
        week.push({ date: day, key: toLocalDateKey(day) });
        if (day.getMonth() !== lastMonth && d === 0) {
          monthLabels.push({
            label: day.toLocaleString("default", { month: "short" }),
            col: w,
          });
          lastMonth = day.getMonth();
        }
        cursor.setDate(cursor.getDate() + 1);
      }
      weeksArr.push(week);
    }

    return { weeks: weeksArr, months: monthLabels };
  }, [projectStart, projectEnd]);

  // Color scale: indigo palette matching the UI
  function getColor(value: number, max: number): string {
    if (value === 0) return "bg-slate-100";
    const ratio = value / max;
    if (ratio < 0.15) return "bg-indigo-100";
    if (ratio < 0.35) return "bg-indigo-300";
    if (ratio < 0.65) return "bg-indigo-500";
    if (ratio < 0.85) return "bg-indigo-600";
    return "bg-indigo-800";
  }

  const maxValue = useMemo(() => {
    const vals = Object.values(dailyData).map((d) =>
      mode === "commits" ? d.commits : d.lines
    );
    return Math.max(1, ...vals);
  }, [dailyData, mode]);

  const dayLabels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

  const totalCommits = Object.values(dailyData).reduce(
    (s, d) => s + d.commits,
    0
  );
  const totalLines = Object.values(dailyData).reduce(
    (s, d) => s + d.lines,
    0
  );

  return (
    <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-5">
      {/* Header row */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <p className="text-sm font-bold text-slate-700">
            {mode === "commits" ? "Commit Activity" : "Lines Added"}
          </p>
          <p className="text-xs text-slate-400 mt-0.5">
            {mode === "commits"
              ? `${totalCommits} commits · ${startLabel} – ${endLabel}`
              : `${totalLines.toLocaleString()} lines added · ${startLabel} – ${endLabel}`}
          </p>
        </div>

        {/* Toggle */}
        <div className="flex bg-slate-100 rounded-lg p-0.5 gap-0.5">
          <button
            onClick={() => setMode("commits")}
            className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${
              mode === "commits"
                ? "bg-white text-indigo-700 shadow-sm"
                : "text-slate-500 hover:text-slate-700"
            }`}
          >
            Commits
          </button>
          <button
            onClick={() => setMode("lines")}
            className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${
              mode === "lines"
                ? "bg-white text-indigo-700 shadow-sm"
                : "text-slate-500 hover:text-slate-700"
            }`}
          >
            Lines Added
          </button>
        </div>
      </div>

      {/* Grid */}
      <div className="overflow-x-auto">
        <div className="min-w-max">
          {/* Month labels — col * COL_WIDTH matches the actual rendered column width */}
          <div className="relative mb-1 ml-8 h-4" style={{ width: `${weeks.length * COL_WIDTH}px` }}>
            {months.map((m, i) => (
              <span
                key={i}
                className="absolute text-xs text-slate-400 font-medium"
                style={{ left: `${m.col * COL_WIDTH}px` }}
              >
                {m.label}
              </span>
            ))}
          </div>

          {/* Day rows */}
          <div className="flex gap-1">
            {/* Day-of-week labels */}
            <div className="flex flex-col gap-0.5 mr-1">
              {dayLabels.map((label, i) => (
                <div
                  key={i}
                  className="h-3 w-6 flex items-center justify-end pr-1"
                >
                  {i % 2 === 1 && (
                    <span className="text-[9px] text-slate-400 font-medium">
                      {label}
                    </span>
                  )}
                </div>
              ))}
            </div>

            {/* Cells */}
            {weeks.map((week, wi) => (
              <div key={wi} className="flex flex-col gap-0.5">
                {week.map(({ date, key }) => {
                  const data = dailyData[key];
                  const value = data
                    ? mode === "commits"
                      ? data.commits
                      : data.lines
                    : 0;
                  return (
                    <div
                      key={key}
                      className={`w-3 h-3 rounded-sm transition-all cursor-default ${getColor(value, maxValue)}`}
                      onMouseEnter={(e) => {
                        const rect = (e.target as HTMLElement).getBoundingClientRect();
                        setTooltip({
                          x: rect.left + rect.width / 2,
                          y: rect.top - 8,
                          date: date.toLocaleDateString("en-US", {
                            month: "short",
                            day: "numeric",
                            year: "numeric",
                          }),
                          value,
                        });
                      }}
                      onMouseLeave={() => setTooltip(null)}
                    />
                  );
                })}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="flex items-center gap-1.5 mt-3 justify-end">
        <span className="text-xs text-slate-400">Less</span>
        {["bg-slate-100", "bg-indigo-100", "bg-indigo-300", "bg-indigo-500", "bg-indigo-700"].map(
          (c, i) => (
            <div key={i} className={`w-3 h-3 rounded-sm ${c}`} />
          )
        )}
        <span className="text-xs text-slate-400">More</span>
      </div>

      {/* Tooltip (fixed position) */}
      {tooltip && (
        <div
          className="fixed z-50 pointer-events-none"
          style={{ left: tooltip.x, top: tooltip.y, transform: "translate(-50%, -100%)" }}
        >
          <div className="bg-slate-800 text-white text-xs rounded-lg px-2.5 py-1.5 shadow-lg whitespace-nowrap">
            <span className="font-semibold">
              {tooltip.value}{" "}
              {mode === "commits"
                ? tooltip.value === 1
                  ? "commit"
                  : "commits"
                : "lines added"}
            </span>
            <span className="text-slate-300 ml-1">on {tooltip.date}</span>
          </div>
          <div className="w-2 h-2 bg-slate-800 rotate-45 mx-auto -mt-1" />
        </div>
      )}
    </div>
  );
}