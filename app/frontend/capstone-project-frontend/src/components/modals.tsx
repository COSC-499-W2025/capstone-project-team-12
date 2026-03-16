import type { ModalProps } from "../types/dashboardTypes";

export function Modal({ title, description, confirmLabel, confirmColor = "red", onConfirm, onCancel }: ModalProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-xl border border-slate-200 w-full max-w-sm mx-4 p-6 space-y-4">
        <h2 className="text-base font-bold text-slate-800">{title}</h2>
        <p className="text-sm text-slate-500 leading-relaxed">{description}</p>
        <div className="flex gap-2 justify-end pt-1">
          <button onClick={onCancel} className="text-xs font-semibold text-slate-500 border border-slate-200 rounded-lg px-4 py-2 hover:bg-slate-50 transition-all">
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className={`text-xs font-bold text-white rounded-lg px-4 py-2 transition-all ${
              confirmColor === "red" ? "bg-red-500 hover:bg-red-600" : "bg-indigo-600 hover:bg-indigo-700"
            }`}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}