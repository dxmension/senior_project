from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Boolean

from app.models.base import Base, IDMixin, TimestampMixin


class User(Base, IDMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True)
    google_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    first_name: Mapped[str] = mapped_column(String(64))
    last_name: Mapped[str] = mapped_column(String(64))

    major: Mapped[str | None] = mapped_column(String(64))
    study_year: Mapped[int | None] = mapped_column()

    avatar_url: Mapped[str | None] = mapped_column(String, nullable=True)

    is_onboarded: Mapped[bool] = mapped_column(Boolean, default=False)

    transcript: Mapped["Transcript | None"] = relationship(
        back_populates="user", uselist=False
    )
    enrollments: Mapped[list["Enrollment"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"<User {self.email}>"
