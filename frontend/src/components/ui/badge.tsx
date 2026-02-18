interface BadgeProps {
  children: React.ReactNode;
  variant?: "green" | "orange" | "red" | "blue" | "muted";
  className?: string;
}

const variantStyles: Record<string, string> = {
  green: "bg-accent-green-dim text-accent-green",
  orange: "bg-accent-orange-dim text-accent-orange",
  red: "bg-accent-red-dim text-accent-red",
  blue: "bg-accent-blue-dim text-accent-blue",
  muted: "bg-bg-card text-text-secondary",
};

export function Badge({ children, variant = "muted", className = "" }: BadgeProps) {
  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium ${variantStyles[variant]} ${className}`}
    >
      {children}
    </span>
  );
}
