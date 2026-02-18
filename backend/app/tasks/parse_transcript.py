import logging

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    name="app.tasks.parse_transcript.parse_transcript_task",
    bind=True,
    max_retries=2,
    default_retry_delay=10,
)
def parse_transcript_task(self, transcript_id: str) -> None:
    from app.database import SessionLocal
    from app.models.transcript import Transcript, TranscriptStatus
    from app.utils.trancript import process_transcript_file

    session = SessionLocal()
    try:
        transcript = session.get(Transcript, int(transcript_id))
        if not transcript:
            logger.error("Transcript %s not found", transcript_id)
            return

        transcript.status = TranscriptStatus.PROCESSING
        session.commit()

        result = process_transcript_file(transcript.file_url, ".pdf")

        if not result.get("success"):
            transcript.status = TranscriptStatus.FAILED
            transcript.error_message = result.get("error", "Unknown parsing error")
            session.commit()
            return

        student_info = result.get("student_info", {})
        courses = result.get("courses", [])

        total_ects = sum(c.get("ects", 0) for c in courses)
        grade_points_sum = sum(
            c.get("grade_points", 0.0) * c.get("ects", 0) for c in courses
        )
        gpa = round(grade_points_sum / total_ects, 2) if total_ects > 0 else None

        transcript.status = TranscriptStatus.COMPLETED
        transcript.raw_text = None
        transcript.major = student_info.get("major")
        transcript.gpa = gpa
        transcript.total_credits_earned = total_ects
        transcript.total_credits_enrolled = total_ects
        transcript.parsed_data = {
            "student_info": student_info,
            "courses": courses,
        }
        transcript.error_message = None
        session.commit()

        logger.info("Transcript %s parsed successfully", transcript_id)

    except Exception as exc:
        session.rollback()
        logger.exception("Failed to parse transcript %s", transcript_id)
        try:
            transcript = session.get(Transcript, int(transcript_id))
            if transcript:
                transcript.status = TranscriptStatus.FAILED
                transcript.error_message = str(exc)
                session.commit()
        except Exception:
            session.rollback()
        raise self.retry(exc=exc, countdown=10 * (2 ** self.request.retries))
    finally:
        session.close()
