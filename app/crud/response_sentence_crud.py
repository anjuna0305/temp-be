from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.db_model import ResponseSentence


async def get_by_source_sentence_id(db: AsyncSession, source_sentence_id: int):
    try:
        result = await db.execute(
            select(ResponseSentence).where(source_sentence_id == ResponseSentence.source_sentence_id)
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


# async def get_by(db: AsyncSession, sentence_id: int):
#     try:
#         result = await db.execute(
#             select(ResponseSentence).where(sentence_id == ResponseSentence.sentence_id)
#         )
#         return result.scalars().first()
#     except Exception as e:
#         raise e
#

async def create(db: AsyncSession, sentence: ResponseSentence):
    try:
        db.add(sentence)
        await db.commit()
        await db.refresh(sentence)
        return sentence
    except Exception as e:
        raise e
