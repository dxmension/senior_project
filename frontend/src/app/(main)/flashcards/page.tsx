"use client";

import { GlassCard } from "@/components/ui/glass-card";
import { Layers } from "lucide-react";

export default function FlashcardsPage() {
  return (
    <div className="space-y-6 max-w-5xl">
      <h1 className="text-2xl font-bold text-text-primary">Flashcards</h1>
      <GlassCard className="flex flex-col items-center py-16">
        <Layers size={40} className="text-text-muted mb-4" />
        <h3 className="text-lg font-semibold text-text-primary">Coming Soon</h3>
        <p className="text-sm text-text-secondary mt-1">
          Spaced repetition flashcards for effective studying
        </p>
      </GlassCard>
    </div>
  );
}
