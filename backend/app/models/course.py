from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Text

from app.models.base import Base, IDMixin


class Course(Base, IDMixin):
    __tablename__ = "courses"

    code: Mapped[str] = mapped_column(String(16))
    level: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(256))
    department: Mapped[str | None] = mapped_column(String(64))
    ects: Mapped[int] = mapped_column(Integer)
    description: Mapped[str | None] = mapped_column(Text)

    enrollments: Mapped[list["Enrollment"]] = relationship(back_populates="course")

    def __repr__(self) -> str:
        return f"<Course(course_id={self.id}, code={self.code}, title={self.title})>"