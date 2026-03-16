from pydantic import BaseModel


class NotificationsPlaceholder(BaseModel):
    message: str = "Notifications feature placeholder"
