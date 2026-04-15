from importlib import import_module
from typing import Any, AsyncGenerator, Generator, Generic, TypeVar

from sqlalchemy import MetaData, QueuePool, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from nutrack.config import settings

ModelT = TypeVar("ModelT")
MODEL_MODULES = (
    "nutrack.assessments.models",
    "nutrack.categories.models",
    "nutrack.courses.models",
    "nutrack.enrollments.models",
    "nutrack.events.models",
    "nutrack.study.models",
    "nutrack.transcripts.models",
    "nutrack.users.models",
)

async_engine = create_async_engine(
    settings.DATABASE_URL,
    poolclass=NullPool,
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

sync_engine = create_engine(
    settings.SYNC_DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    echo=False,
)

SessionLocal = sessionmaker(bind=sync_engine, expire_on_commit=False)


class BaseRepository(Generic[ModelT]):
    def __init__(self, session: AsyncSession, model: type[ModelT]) -> None:
        self.session = session
        self.model = model

    async def get_by_id(self, entity_id: int) -> ModelT | None:
        return await self.session.get(self.model, entity_id)

    async def create(self, **data: Any) -> ModelT:
        entity = self.model(**data)
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def update(self, entity: ModelT, **data: Any) -> ModelT:
        for field, value in data.items():
            setattr(entity, field, value)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def delete(self, entity: ModelT) -> None:
        await self.session.delete(entity)
        await self.session.flush()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_sync_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_sync_database_url() -> str:
    return settings.SYNC_DATABASE_URL


def load_model_modules() -> None:
    for module_name in MODEL_MODULES:
        import_module(module_name)


def load_target_metadata() -> MetaData:
    load_model_modules()
    from nutrack.models import Base

    return Base.metadata
