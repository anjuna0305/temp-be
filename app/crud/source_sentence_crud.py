from sqlalchemy import select, desc
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
            select(SourceSentence)
            .where(project_id == SourceSentence.project_id)
            .order_by(desc(SourceSentence.sentence_id))
        )
        return result.scalars().all()
    except Exception as e:
        raise e


async def get_by_id(db: AsyncSession, sentence_id: int) -> SourceSentence:
    try:
        result = await db.execute(
            select(SourceSentence).where(sentence_id == SourceSentence.sentence_id)
        )
        return result.scalars().first()
    except Exception as e:
        raise e


async def get_first_of_project(db: AsyncSession, project_id: int):
    try:
        result = await db.execute(
            select(SourceSentence).where(project_id == SourceSentence.project_id).order_by(
                SourceSentence.sentence_id)
        )
        return result.scalars().first()
    except Exception as e:
        raise e

# async def get_by_sentence_id_and_user_id(db:AsyncSession, sentence)


async def create(db: AsyncSession, sentence: SourceSentence):
    try:
        db.add(sentence)
        await db.commit()
        await db.refresh(sentence)
        return sentence
    except Exception as e:
        raise e
