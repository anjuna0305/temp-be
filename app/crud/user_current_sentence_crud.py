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


async def mark_as_replied(db: AsyncSession, user_id: int, project_id: int):
    try:
        result = await db.execute(
            select(UserCurrentSentence).where(
                and_(user_id == UserCurrentSentence.user_id, project_id == UserCurrentSentence.project_id))
        )
        record = result.scalars().first()
        if record:
            record.is_answered = True
            await db.commit()
            return True
        else:
            return False

    except Exception as e:
        print("there is a catch \n\n\n\n\n\n\n")
        raise e


async def create(db: AsyncSession, user_id: int, project_id: int, sentence_id: int):
    try:
        user_current_sentence = UserCurrentSentence(
            user_id=user_id,
            project_id=project_id,
            sentence_id=sentence_id,
            is_answered=False
        )
        db.add(user_current_sentence)
        await db.commit()
        await db.refresh(user_current_sentence)
        return user_current_sentence
    except Exception as e:
        raise e


async def update(db: AsyncSession, user_id: int, project_id: int, new_sentence_id: int, ):
    try:
        result = await db.execute(
            select(UserCurrentSentence).where(
                and_(user_id == UserCurrentSentence.user_id, project_id == UserCurrentSentence.project_id))
        )
        record = result.scalars().first()
        if record:
            record.sentence_id = new_sentence_id
            record.is_answered = False
            await db.commit()
            return True

    except Exception as e:
        raise e
