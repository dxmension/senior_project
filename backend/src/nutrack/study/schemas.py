from pydantic import BaseModel


class StudyPlaceholder(BaseModel):
    message: str = "Study feature placeholder"
