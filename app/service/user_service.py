from sqlalchemy.ext.asyncio import AsyncSession

import app.crud.response_sentence_crud as response_sentence_crud
import app.crud.source_sentence_crud as source_sentence_crud
import app.crud.user_current_sentence_crud as current_sentence_crud
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
            raise NotFoundError(detail="No source sentence found for the given id.")
        project_id = source_sentence.project_id

        project_sentences = await source_sentence_crud.get_by_project_id(db, project_id)
        if not project_sentences:
            raise InternalServerError(detail="Problem with project data.")

        index_of_source = project_sentences.index(source_sentence)
        if index_of_source == 0:
            raise NotFoundError(detail="No more sentences in the project.")
        return project_sentences[index_of_source - 1].sentence_id

    except Exception as e:
        print(f"exception while generating next sentence id: {e}")
        return None


async def create_new_response(
        db: AsyncSession, req_data: CreateResponseSentenceRequest, user: User
):
    try:
        allowed_sentence_id = await current_sentence_crud.get_by_source_id(db, user.id, req_data.project_id)
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


async def get_source_sentence(db: AsyncSession, project_id: int, user: User) -> SourceSentence:
    try:
        # check for ongoing sentence id in database
        ongoing_source_id = await current_sentence_crud.get_by_source_id(db, user.id, project_id)

        # if ongoing id exit in database
        if ongoing_source_id:
            # if source id exist, fetch source sentence
            source_sentence = await source_sentence_crud.get_by_id(
                db, ongoing_source_id
            )
            # generate next source id and store it
            next_id = await get_next_source_id(db, ongoing_source_id)
            if next_id:
                await current_sentence_crud.create(db, user.id, project_id, next_id)
            else:
                await current_sentence_crud.create(db, user.id, project_id, ongoing_source_id + 1)
            # return source sentence
            return source_sentence

        # if not ongoing sentence id in database, check last response and find next source id
        last_response_id = await response_sentence_crud.get_last_source_id_by_user_id(
            db, user.id
        )
        if last_response_id:  # if last response id exist
            next_id = await get_next_source_id(db, last_response_id.source_sentence_id)
            if next_id:
                await current_sentence_crud.create(db, user.id, project_id, next_id)
                source
            else:
                await current_sentence_crud.create(db, user.id, project_id, last_response_id.source_sentence_id + 1)
        else:  # if there are no responses, first sentence of the project will return
            first_sentence = await source_sentence_crud.get_first_of_project(db, project_id)
            if first_sentence:  # if first sentence exist save current sentence id in db and return sentence
                await current_sentence_crud.create(db, user.id, project_id, first_sentence.sentence_id)
                return first_sentence
            else:
                raise NotFoundError(detail="First sentence of project not found.")

    except Exception as e:
        raise e


async def get_new_source_sentence(db: AsyncSession, user: User):
    try:
        ongoing_source_id = redis_db.get_value(user.id)
        if ongoing_source_id:
            source_sentence = await source_sentence_crud.get_by_id(
                db, ongoing_source_id
            )
            next_sentence_id = await get_next_source_id(db, ongoing_source_id)
            next_sentence = await source_sentence_crud.get_by_id(db, next_sentence_id)
            if not next_sentence_id or next_sentence:
                raise NotFoundError(detail="New sentence not found!")

            redis_db.set_value(user.id, next_sentence_id)
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

        redis_db.set_value(user.id, next_sentence_id)
        return

    except Exception as e:
        raise e
