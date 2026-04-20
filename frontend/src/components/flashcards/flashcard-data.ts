export interface Flashcard {
  id: number;
  question: string;
  answer: string;
}

export type Difficulty = "easy" | "okay" | "hard";
