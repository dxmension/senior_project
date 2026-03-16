from sqlalchemy import Boolean, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from nutrack.models import Base, IDMixin, TimestampMixin


class User(Base, IDMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True)
    google_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    first_name: Mapped[str] = mapped_column(String(64))
    last_name: Mapped[str] = mapped_column(String(64))

    major: Mapped[str | None] = mapped_column(String(64))
    study_year: Mapped[int | None] = mapped_column(Integer)
    cgpa: Mapped[float | None] = mapped_column(Float, nullable=True)

    total_credits_earned: Mapped[int | None] = mapped_column(Integer)
    total_credits_enrolled: Mapped[int | None] = mapped_column(Integer)

    avatar_url: Mapped[str | None] = mapped_column(String, nullable=True)
    is_onboarded: Mapped[bool] = mapped_column(Boolean, default=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    enrollments: Mapped[list["Enrollment"]] = relationship(
        back_populates="user",
    )

    def __repr__(self) -> str:
        return f"<User {self.email}>"
