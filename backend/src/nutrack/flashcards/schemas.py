from pydantic import BaseModel


class FlashcardItem(BaseModel):
    id: int
    question: str
    answer: str


class FlashcardsPlaceholder(BaseModel):
    message: str = "Flashcards feature placeholder"
