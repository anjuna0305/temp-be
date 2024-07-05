from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.db_model import UserCurrentSentence


async def get_by_user_id(db: AsyncSession, user_id: int):
    try:
        result = await db.execute(
            select(UserCurrentSentence).where(user_id == UserCurrentSentence.user_id)
        )
        return result.scalars().all()
    except Exception as e:
        raise e


async def get_by_source_id(db: AsyncSession, user_id: int, project_id: int):
    try:
        result = await db.execute(
            select(UserCurrentSentence).where(
                and_(user_id == UserCurrentSentence.user_id, project_id == UserCurrentSentence.project_id))
        )
        return result.scalars().first()
    except Exception as e:
        raise e


async def create(db: AsyncSession, user_id: int, project_id: int, sentence_id: int):
    try:
        user_current_sentence = UserCurrentSentence(
            user_id=user_id,
            project_id=project_id,
            sentence_id=sentence_id
        )
        db.add(user_current_sentence)
        await db.commit()
        await db.refresh(user_current_sentence)
        return user_current_sentence
    except Exception as e:
        raise e
