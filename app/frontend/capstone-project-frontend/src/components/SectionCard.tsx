import type { ReactNode } from "react";

interface SectionCardProps {
  title: string;
  icon: string;
  children: ReactNode;
}

export default function SectionCard({ title, icon, children }: SectionCardProps) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
      <div className="px-5 py-4 border-b border-slate-100 flex items-center gap-2">
        <span className="text-lg">{icon}</span>
        <h2 className="font-bold text-slate-700 text-sm uppercase tracking-wider">{title}</h2>
      </div>
      <div className="p-5">{children}</div>
    </div>
  );
}
