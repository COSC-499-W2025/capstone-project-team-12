interface StatCardProps {
  label: string;
  value: string | number;
  sub?: string;
  accent?: boolean;
}

export default function StatCard({ label, value, sub, accent }: StatCardProps) {
  return (
    <div className={`relative rounded-2xl p-5 bg-white border ${accent ? "border-indigo-300" : "border-slate-200"} shadow-sm flex flex-col gap-1 overflow-hidden`}>
      {accent && <div className="absolute inset-0 bg-indigo-50 opacity-40 pointer-events-none" />}
      <span className={`text-3xl font-bold ${accent ? "text-indigo-700" : "text-slate-800"}`}>{value}</span>
      <span className="text-xs font-semibold uppercase tracking-widest text-slate-400">{label}</span>
      {sub && <span className="text-xs text-slate-500 mt-0.5">{sub}</span>}
    </div>
  );
}
