"""normalize courses into offerings

Revision ID: 6a9275f1d8c4
Revises: 9b3f4c2d1a10
Create Date: 2026-03-18 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "6a9275f1d8c4"
down_revision: Union[str, None] = "9b3f4c2d1a10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _drop_course_fk(target_table: str) -> None:
    op.execute(
        f"""
        DO $$
        DECLARE
            constraint_name text;
        BEGIN
            SELECT conname
            INTO constraint_name
            FROM pg_constraint
            WHERE conrelid = '{target_table}'::regclass
              AND contype = 'f'
              AND confrelid IN ('courses'::regclass, 'course_offerings'::regclass)
            LIMIT 1;

            IF constraint_name IS NOT NULL THEN
                EXECUTE format(
                    'ALTER TABLE {target_table} DROP CONSTRAINT %I',
                    constraint_name
                );
            END IF;
        END
        $$;
        """
    )


def upgrade() -> None:
    op.create_table(
        "course_offerings",
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("term", sa.String(length=16), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("section", sa.String(length=16), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("days", sa.String(length=64), nullable=True),
        sa.Column("meeting_time", sa.String(length=64), nullable=True),
        sa.Column("enrolled", sa.Integer(), nullable=True),
        sa.Column("capacity", sa.Integer(), nullable=True),
        sa.Column("faculty", sa.Text(), nullable=True),
        sa.Column("room", sa.String(length=128), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "course_id",
            "term",
            "year",
            "section",
            name="uq_course_offerings_course_term_year_section",
        ),
    )
    op.create_index(
        op.f("ix_course_offerings_id"),
        "course_offerings",
        ["id"],
        unique=True,
    )

    op.create_table(
        "course_identity_map",
        sa.Column("legacy_id", sa.Integer(), nullable=False),
        sa.Column("canonical_id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("legacy_id"),
    )
    op.execute(
        """
        INSERT INTO course_identity_map (legacy_id, canonical_id)
        SELECT
            id AS legacy_id,
            first_value(id) OVER (
                PARTITION BY code, level
                ORDER BY year DESC,
                    CASE term
                        WHEN 'Fall' THEN 3
                        WHEN 'Summer' THEN 2
                        WHEN 'Spring' THEN 1
                        ELSE 0
                    END DESC,
                    id DESC
            ) AS canonical_id
        FROM courses
        """
    )
    op.execute(
        """
        INSERT INTO course_offerings (
            id,
            course_id,
            term,
            year,
            section,
            start_date,
            end_date,
            days,
            meeting_time,
            enrolled,
            capacity,
            faculty,
            room
        )
        SELECT
            courses.id,
            course_identity_map.canonical_id,
            courses.term,
            courses.year,
            courses.section,
            courses.start_date,
            courses.end_date,
            courses.days,
            courses.meeting_time,
            courses.enrolled,
            courses.capacity,
            courses.faculty,
            courses.room
        FROM courses
        JOIN course_identity_map
          ON course_identity_map.legacy_id = courses.id
        """
    )

    _drop_course_fk("enrollments")
    op.create_foreign_key(
        "fk_enrollments_course_offering_id",
        "enrollments",
        "course_offerings",
        ["course_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.execute(
        """
        DELETE FROM courses
        USING course_identity_map
        WHERE courses.id = course_identity_map.legacy_id
          AND course_identity_map.legacy_id <> course_identity_map.canonical_id
        """
    )
    op.drop_constraint(
        "uq_courses_code_level_section_term_year",
        "courses",
        type_="unique",
    )
    op.create_unique_constraint(
        "uq_courses_code_level",
        "courses",
        ["code", "level"],
    )
    op.drop_column("courses", "section")
    op.drop_column("courses", "term")
    op.drop_column("courses", "year")
    op.drop_column("courses", "start_date")
    op.drop_column("courses", "end_date")
    op.drop_column("courses", "days")
    op.drop_column("courses", "meeting_time")
    op.drop_column("courses", "enrolled")
    op.drop_column("courses", "capacity")
    op.drop_column("courses", "faculty")
    op.drop_column("courses", "room")

    op.execute("DROP TABLE course_identity_map")
    op.execute(
        """
        SELECT setval(
            pg_get_serial_sequence('course_offerings', 'id'),
            COALESCE((SELECT MAX(id) FROM course_offerings), 1),
            true
        )
        """
    )


def downgrade() -> None:
    op.create_table(
        "courses_restored",
        sa.Column("code", sa.String(length=16), nullable=False),
        sa.Column("level", sa.String(length=16), nullable=False),
        sa.Column("title", sa.String(length=256), nullable=False),
        sa.Column("department", sa.String(length=64), nullable=True),
        sa.Column("ects", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("pass_grade", sa.String(), nullable=True),
        sa.Column("school", sa.String(length=32), nullable=True),
        sa.Column("academic_level", sa.String(length=16), nullable=True),
        sa.Column("section", sa.String(length=16), nullable=True),
        sa.Column("credits_us", sa.Float(), nullable=True),
        sa.Column("term", sa.String(length=16), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("days", sa.String(length=64), nullable=True),
        sa.Column("meeting_time", sa.String(length=64), nullable=True),
        sa.Column("enrolled", sa.Integer(), nullable=True),
        sa.Column("capacity", sa.Integer(), nullable=True),
        sa.Column("faculty", sa.Text(), nullable=True),
        sa.Column("room", sa.String(length=128), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.execute(
        """
        INSERT INTO courses_restored (
            id,
            code,
            level,
            title,
            department,
            ects,
            description,
            pass_grade,
            school,
            academic_level,
            section,
            credits_us,
            term,
            year,
            start_date,
            end_date,
            days,
            meeting_time,
            enrolled,
            capacity,
            faculty,
            room
        )
        SELECT
            course_offerings.id,
            courses.code,
            courses.level,
            courses.title,
            courses.department,
            courses.ects,
            courses.description,
            courses.pass_grade,
            courses.school,
            courses.academic_level,
            course_offerings.section,
            courses.credits_us,
            course_offerings.term,
            course_offerings.year,
            course_offerings.start_date,
            course_offerings.end_date,
            course_offerings.days,
            course_offerings.meeting_time,
            course_offerings.enrolled,
            course_offerings.capacity,
            course_offerings.faculty,
            course_offerings.room
        FROM course_offerings
        JOIN courses
          ON courses.id = course_offerings.course_id
        """
    )

    _drop_course_fk("enrollments")
    op.drop_constraint(
        "uq_courses_code_level",
        "courses",
        type_="unique",
    )
    op.drop_index(op.f("ix_course_offerings_id"), table_name="course_offerings")
    op.drop_table("course_offerings")
    op.drop_index(op.f("ix_courses_id"), table_name="courses")
    op.drop_table("courses")

    op.rename_table("courses_restored", "courses")
    op.create_index(op.f("ix_courses_id"), "courses", ["id"], unique=True)
    op.create_unique_constraint(
        "uq_courses_code_level_section_term_year",
        "courses",
        ["code", "level", "section", "term", "year"],
    )
    op.create_foreign_key(
        "fk_enrollments_course_id",
        "enrollments",
        "courses",
        ["course_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.execute(
        """
        SELECT setval(
            pg_get_serial_sequence('courses', 'id'),
            COALESCE((SELECT MAX(id) FROM courses), 1),
            true
        )
        """
    )
