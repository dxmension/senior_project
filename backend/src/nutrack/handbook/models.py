from sqlalchemy import Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from nutrack.models import Base, IDMixin, TimestampMixin


class HandbookPlan(Base, IDMixin, TimestampMixin):
    """
    Stores the parsed degree-requirement plan from an uploaded Academic Handbook PDF.
    One record per enrollment year.  status flow: processing → completed | failed.
    plans JSON structure mirrors DegreePlan: { major_key: { total_ects, categories: [...] } }
    """
    __tablename__ = "handbook_plans"
    __table_args__ = (
        UniqueConstraint("enrollment_year", name="uq_handbook_plans_year"),
    )

    enrollment_year: Mapped[int] = mapped_column(Integer, nullable=False)
    filename: Mapped[str] = mapped_column(String(256), nullable=False)
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="processing"
    )  # "processing" | "completed" | "failed"
    plans: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
