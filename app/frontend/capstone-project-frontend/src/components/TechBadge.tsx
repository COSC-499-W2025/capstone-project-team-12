interface TechBadgeProps {
  name: string;
  uses: number;
}

export default function TechBadge({ name, uses }: TechBadgeProps) {
  const intensity =
    uses >= 10 ? "bg-indigo-700 text-white" :
    uses >= 8  ? "bg-indigo-500 text-white" :
    uses >= 6  ? "bg-indigo-300 text-indigo-900" :
                 "bg-indigo-100 text-indigo-600";
  return (
    <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold ${intensity}`}>
      {name}<span className="opacity-60 font-normal">{uses}×</span>
    </span>
  );
}
