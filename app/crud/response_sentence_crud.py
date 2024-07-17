from sqlalchemy import select, desc, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.db_model import ResponseSentence


async def get_by_source_sentence_id(db: AsyncSession, source_sentence_id: int):
    try:
        result = await db.execute(
            select(ResponseSentence).where(
                source_sentence_id == ResponseSentence.source_sentence_id
            )
        )
        return result.scalars().all()
    except Exception as e:
        raise e


async def get_by_id(db: AsyncSession, response_id: int):
    try:
        result = await db.execute(
            select(ResponseSentence).where(response_id == ResponseSentence.sentence_id)
        )
        return result.scalars().all()
    except Exception as e:
        raise e


async def get_by_user_id(
        db: AsyncSession, user_id: int, limit_value: int = 20, offset_value: int = 0
):
    try:
        result = await db.execute(
            select(ResponseSentence)
            .where(user_id == ResponseSentence.user_id)
            .order_by(desc(ResponseSentence.created_at))
            .limit(limit_value)
            .offset(offset_value)
        )
        return result.scalars().all()
    except Exception as e:
        raise e


async def get_last_source_id_by_user_id(db: AsyncSession, user_id: int):
    try:
        result = await db.execute(
            select(ResponseSentence)
            .where(user_id == ResponseSentence.user_id)
            .order_by(desc(ResponseSentence.created_at))
        )
        return result.scalars().first()
    except Exception as e:
        raise e


async def get_by_user_id_and_source_id(db: AsyncSession, source_id: int, user_id: int):
    try:
        result = await db.execute(
            select(ResponseSentence).where(
                and_(
                    source_id == ResponseSentence.source_sentence_id,
                    user_id == ResponseSentence.user_id,
                )
            )
        )
        return result.scalars().first()
    except Exception as e:
        raise e


async def get_by_user_id_and_project_id(db: AsyncSession, project_id: int, user_id: int, limit_value: int = 20,
                                        offset_value: int = 0):
    try:
        result = await db.execute(
            select(ResponseSentence).where(
                and_(
                    project_id == ResponseSentence.project_id,
                    user_id == ResponseSentence.user_id,
                )
            )
            .order_by(desc(ResponseSentence.source_sentence_id))
            .limit(limit_value)
            .offset(offset_value)
        )
        return result.scalars().all()
    except Exception as e:
        raise e


async def create(db: AsyncSession, sentence: ResponseSentence):
    try:
        db.add(sentence)
        await db.commit()
        await db.refresh(sentence)
        return sentence
    except Exception as e:
        raise e


async def get_response_count(db: AsyncSession, project_id: int):
    try:
        stmt = select(func.count()).where(ResponseSentence.project_id == project_id)
        result = await db.execute(stmt)
        count = result.scalar()
        return count
    except Exception as e:
        raise e
