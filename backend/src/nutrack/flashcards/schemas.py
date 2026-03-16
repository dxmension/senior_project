from pydantic import BaseModel


class FlashcardsPlaceholder(BaseModel):
    message: str = "Flashcards feature placeholder"
