import { Check, Minus, X } from "lucide-react";
import type { Difficulty } from "./flashcard-data";

interface DifficultyButtonsProps {
  visible: boolean;
  onRate: (rating: Difficulty) => void;
}

const buttons: {
  rating: Difficulty;
  label: string;
  icon: typeof Check;
  classes: string;
}[] = [
  {
    rating: "easy",
    label: "Easy",
    icon: Check,
    classes: "text-accent-green bg-accent-green/10 hover:bg-accent-green/20",
  },
  {
    rating: "okay",
    label: "Okay",
    icon: Minus,
    classes: "text-accent-orange bg-accent-orange/10 hover:bg-accent-orange/20",
  },
  {
    rating: "hard",
    label: "Hard",
    icon: X,
    classes: "text-accent-red bg-accent-red/10 hover:bg-accent-red/20",
  },
];

export function DifficultyButtons({ visible, onRate }: DifficultyButtonsProps) {
  return (
    <div
      className={`flex items-center justify-center gap-3 transition-opacity duration-300 ${
        visible ? "opacity-100" : "pointer-events-none opacity-0"
      }`}
    >
      {buttons.map(({ rating, label, icon: Icon, classes }) => (
        <button
          key={rating}
          type="button"
          onClick={() => onRate(rating)}
          className={`inline-flex items-center gap-2 rounded-lg px-5 py-2.5 text-sm font-medium transition-transform active:scale-95 ${classes}`}
        >
          <Icon size={16} />
          {label}
        </button>
      ))}
    </div>
  );
}
