from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.db_model import SourceSentence


async def get_by_sentence(db: AsyncSession, sentence: str):
    try:
        result = await db.execute(
            select(SourceSentence).where(sentence == SourceSentence.source_sentence)
        )
        return result.scalars().all()
    except Exception as e:
        raise e


async def get_by_project_id(db: AsyncSession, project_id: int):
    try:
        result = await db.execute(
            select(SourceSentence).where(project_id == SourceSentence.project_id)
        )
        return result.scalars().all()
    except Exception as e:
        raise e


async def get_by_id(db: AsyncSession, sentence_id: int):
    try:
        result = await db.execute(
            select(SourceSentence).where(sentence_id == SourceSentence.sentence_id)
        )
        return result.scalars().first()
    except Exception as e:
        raise e


async def create(db: AsyncSession, sentence: SourceSentence):
    try:
        db.add(sentence)
        await db.commit()
        await db.refresh(sentence)
        return sentence
    except Exception as e:
        raise e
