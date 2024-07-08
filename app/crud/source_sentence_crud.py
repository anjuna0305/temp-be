from sqlalchemy import select, desc, and_
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


async def get_next_sentence_id(db: AsyncSession, project_id: int, current_sentence_id: int):
    # Step 1: Query for the current SourceSentence

    current_sentence = await get_by_id(db, current_sentence_id)

    if current_sentence:
        # Step 2: Query for the next SourceSentence
        next_sentences = await db.execute(
            select(SourceSentence).where(and_(SourceSentence.sentence_id > current_sentence_id,
                                              SourceSentence.project_id == project_id)).order_by(
                SourceSentence.sentence_id.asc()))
        next_sentence = next_sentences.scalars().first()

        if next_sentence:
            return next_sentence.sentence_id
        else:
            return current_sentence_id
    else:
        print(f"SourceSentence with sentence_id={current_sentence_id} not found.")


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
