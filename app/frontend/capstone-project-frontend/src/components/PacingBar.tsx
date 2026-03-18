interface PacingBarProps {
  percent: number;
  message: string;
}

export default function PacingBar({ percent, message }: PacingBarProps) {
  return (
    <div className="mt-1">
      <div className="flex justify-between text-xs text-slate-400 mb-1.5">
        <span>Start of project</span><span>End of project</span>
      </div>
      <div className="h-3 rounded-full bg-slate-100 overflow-hidden relative">
        <div
          className="absolute right-0 h-full rounded-full bg-gradient-to-r from-indigo-300 to-indigo-600"
          style={{ width: `${percent}%` }}
        />
      </div>
      <p className="text-xs text-slate-500 mt-2">{message}</p>
    </div>
  );
}
