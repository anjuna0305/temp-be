from sqlalchemy.ext.asyncio import AsyncSession

import app.crud.response_sentence_crud as response_sentence_crud
import app.crud.source_sentence_crud as source_sentence_crud
from app.config.database.redis_config import store_value_redis, get_stored_value_redis
from app.exception import (
    BadRequestError,
    InternalServerError,
    ConflictError,
    NotFoundError,
)
from app.model.db_model import User, SourceSentence
from app.schema.request.request_schema import CreateResponseSentenceRequest
from app.schema.request.request_schema_map import (
    create_response_sentence_request_to_response_sentence,
)


async def get_next_source_id(db, source_id: int) -> int | None:
    try:
        source_sentence = await source_sentence_crud.get_by_id(db, source_id)
        if not source_sentence:
            raise Exception
        project_id = source_sentence.project_id

        project_sentences = await source_sentence_crud.get_by_project_id(db, project_id)
        if not project_sentences:
            raise Exception

        index_of_next_source = project_sentences.index(source_sentence)
        if index_of_next_source == 0:
            raise Exception
        return project_sentences[index_of_next_source - 1].sentence_id

    except Exception:
        return None


async def create_new_response(
        db: AsyncSession, req_data: CreateResponseSentenceRequest, user: User
):
    try:
        allowed_sentence_id = int(await get_stored_value_redis(user.id))
        if not allowed_sentence_id or allowed_sentence_id != req_data.source_id:
            raise BadRequestError(detail="Not allowed to response this sentence.")

        source_sentence = await source_sentence_crud.get_by_id(db, req_data.source_id)
        if not source_sentence:
            raise BadRequestError(detail="Invalid source sentence id.")
        if source_sentence.project_id != req_data.project_id:
            raise BadRequestError(
                detail="Source sentence id and project id does not match."
            )

        existing_response = await response_sentence_crud.get_by_user_id_and_source_id(
            db, req_data.source_id, user.id
        )
        if existing_response:
            raise ConflictError(detail="Response already exist")

        response_sentence_obj = create_response_sentence_request_to_response_sentence(
            req_data, user.id
        )
        response = await response_sentence_crud.create(db, response_sentence_obj)
        if not response:
            raise InternalServerError()
        return response
    except Exception as e:
        raise e


async def get_response_sentence_by_user_id(
        db: AsyncSession, user_id: int, limit: int, skip: int
):
    try:
        results = await response_sentence_crud.get_by_user_id(db, user_id, limit, skip)
        return results
    except Exception as e:
        raise e


async def get_source_sentence(db: AsyncSession, user: User) -> SourceSentence:
    try:
        ongoing_source_id = int(await get_stored_value_redis(user.id))
        if ongoing_source_id:
            source_sentence = await source_sentence_crud.get_by_id(
                db, ongoing_source_id
            )
            await store_value_redis(user.id, ongoing_source_id + 1)
            return source_sentence

        ongoing_id = await response_sentence_crud.get_last_source_id_by_user_id(
            db, user.id
        )
        if not ongoing_id:
            raise InternalServerError()

        source_sentence = await source_sentence_crud.get_by_id(db, ongoing_id)
        if not source_sentence:
            raise BadRequestError(detail="No source sentence found.")

        await store_value_redis(user.id, source_sentence.sentence_id)
        return source_sentence
    except Exception as e:
        raise e


async def get_new_source_sentence(db: AsyncSession, user: User):
    try:
        ongoing_source_id = int(await get_stored_value_redis(user.id))
        if ongoing_source_id:
            source_sentence = await source_sentence_crud.get_by_id(
                db, ongoing_source_id
            )
            next_sentence_id = await get_next_source_id(db, ongoing_source_id)
            next_sentence = await source_sentence_crud.get_by_id(db, next_sentence_id)
            if not next_sentence_id or next_sentence:
                raise NotFoundError(detail="New sentence not found!")

            await store_value_redis(user.id, next_sentence_id)
            return next_sentence

        ongoing_id = await response_sentence_crud.get_last_source_id_by_user_id(
            db, user.id
        )
        if not ongoing_id:
            raise InternalServerError()

        next_sentence_id = await get_next_source_id(db, ongoing_id)
        if not next_sentence_id:
            raise NotFoundError(detail="New sentence not found!")

        next_sentence = await source_sentence_crud.get_by_id(db, next_sentence_id)
        if not next_sentence:
            raise NotFoundError(detail="New sentence not found!")

        await store_value_redis(user.id, next_sentence_id)
        return

    except Exception as e:
        raise e
