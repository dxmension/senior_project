"use client";

import { useEffect } from "react";
import { AlertTriangle, X } from "lucide-react";

interface ConfirmDialogProps {
  isOpen: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  variant?: "danger" | "default";
  onConfirm: () => void;
  onCancel: () => void;
}

export function ConfirmDialog({
  isOpen,
  title,
  message,
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  variant = "default",
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (!isOpen) return;
      if (e.key === "Escape") onCancel();
      if (e.key === "Enter") onConfirm();
    };
    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, [isOpen, onCancel, onConfirm]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm"
      onClick={(e) => e.target === e.currentTarget && onCancel()}
    >
      <div className="relative glass-card p-6 w-full max-w-sm shadow-2xl">
        <button
          onClick={onCancel}
          aria-label="Close"
          className="absolute top-4 right-4 rounded-lg p-1.5 text-text-secondary hover:bg-white/5 hover:text-text-primary transition-colors"
        >
          <X size={16} />
        </button>

        <div className="flex items-start gap-4 mb-5">
          <div
            className={`flex-shrink-0 p-2 rounded-lg ${
              variant === "danger"
                ? "bg-accent-red-dim text-accent-red"
                : "bg-accent-green-dim text-accent-green"
            }`}
          >
            <AlertTriangle size={20} />
          </div>
          <div>
            <h3 className="text-base font-semibold text-text-primary">{title}</h3>
            <p className="text-sm text-text-secondary mt-1">{message}</p>
          </div>
        </div>

        <div className="flex gap-3 justify-end">
          <button
            onClick={onCancel}
            className="btn-secondary px-4 py-2 text-sm"
          >
            {cancelLabel}
          </button>
          <button
            onClick={onConfirm}
            className={`px-4 py-2 text-sm font-semibold rounded-lg transition-opacity hover:opacity-90 ${
              variant === "danger"
                ? "bg-accent-red text-bg-primary"
                : "bg-accent-green text-bg-primary"
            }`}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
