import { Loader2 } from "lucide-react";

interface SpinnerProps {
  size?: number;
  className?: string;
  text?: string;
}

export function Spinner({ size = 24, className = "", text }: SpinnerProps) {
  return (
    <div className={`flex flex-col items-center justify-center gap-3 ${className}`}>
      <Loader2 size={size} className="animate-spin text-accent-green" />
      {text && <p className="text-sm text-text-secondary">{text}</p>}
    </div>
  );
}
