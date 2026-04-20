from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.mock_exams.service import MockExamService


class FlashcardsService:
    def __init__(self, session: AsyncSession) -> None:
        self._mock_exam_service = MockExamService(session=session)

    async def get_mock_exam_flashcards(
        self, user_id: int, mock_exam_id: int
    ) -> list[dict]:
        return await self._mock_exam_service.get_mock_exam_flashcards(
            user_id, mock_exam_id
        )
