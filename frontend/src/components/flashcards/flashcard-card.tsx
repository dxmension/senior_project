import type { Flashcard } from "./flashcard-data";

interface FlashcardCardProps {
  card: Flashcard;
  isFlipped: boolean;
  onFlip: () => void;
}

export function FlashcardCard({ card, isFlipped, onFlip }: FlashcardCardProps) {
  return (
    <div
      className="mx-auto w-full max-w-[600px] cursor-pointer"
      style={{ perspective: 1000 }}
      onClick={onFlip}
    >
      <div
        className="relative min-h-[320px] transition-transform duration-500"
        style={{
          transformStyle: "preserve-3d",
          transform: isFlipped ? "rotateY(180deg)" : "rotateY(0deg)",
        }}
      >
        {/* Front */}
        <div
          className="absolute inset-0 flex flex-col items-center justify-center rounded-[var(--radius-lg)] border border-[var(--border-primary)] bg-[#1a1a1a] p-8"
          style={{ backfaceVisibility: "hidden" }}
        >
          <p className="text-center text-lg font-medium text-text-primary">
            {card.question}
          </p>
          <p className="mt-6 text-xs text-text-muted">Space Bar or click to reveal answer</p>
        </div>

        {/* Back */}
        <div
          className="absolute inset-0 flex flex-col items-center justify-center rounded-[var(--radius-lg)] border border-[var(--border-primary)] bg-[#1a1a1a] p-8"
          style={{
            backfaceVisibility: "hidden",
            transform: "rotateY(180deg)",
          }}
        >
          <p className="text-center text-sm leading-relaxed text-text-secondary">
            {card.answer}
          </p>
        </div>
      </div>
    </div>
  );
}
