interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  padding?: boolean;
}

export function GlassCard({ children, className = "", padding = true }: GlassCardProps) {
  return (
    <div className={`glass-card ${padding ? "p-6" : ""} ${className}`}>
      {children}
    </div>
  );
}
