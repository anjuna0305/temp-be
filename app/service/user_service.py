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

async def get_sentence_by_id(db:AsyncSession, source_id:int):
    try:
        sentence = await source_sentence_crud.get_by_id(db, source_id)
        return sentence
    except Exception as e:
        raise e


async def get_next_source_id(db: AsyncSession, source_id: int) -> int | None:
    try:
        source_sentence = await source_sentence_crud.get_by_id(db, source_id)
        if not source_sentence:
            raise NotFoundError(detail="No source sentence found for the given id.")
        project_id = source_sentence.project_id

        next_id = await source_sentence_crud.get_next_sentence_id(db, project_id, source_id)
        return next_id

        # project_sentences = await source_sentence_crud.get_by_project_id(db, project_id)
        # for x in range(len(project_sentences)):
        #     print(project_sentences[x].sentence_id)
        #
        # if not project_sentences:
        #     raise InternalServerError(detail="Problem with project data.")
        #
        # index_of_source = project_sentences.index(source_sentence)
        # print(f"index is: {index_of_source}\n\n\n\n\n\n\n\n")
        # if index_of_source == 0:
        #     raise NotFoundError(detail="No more sentences in the project.")
        # return project_sentences[index_of_source - 1].sentence_id

    except Exception as e:
        print(f"exception while generating next sentence id: {e}")
        return None


async def update_ongoing_sentence(db: AsyncSession, user_id: int, project_id: int, new_sentence_id: int):
    try:
        print("**** update_ongoing_sentence **** : ")
        current_record = await current_sentence_crud.get_by_source_id(db, user_id, project_id)
        if current_record:
            print("**** update_ongoing_sentence **** : current record")
            await current_sentence_crud.update(db, user_id, project_id, new_sentence_id)
        else:
            print("**** update_ongoing_sentence **** : else")
            await current_sentence_crud.create(db, user_id, project_id, new_sentence_id)
        return True
    except Exception as e:
        raise e


async def create_new_response(
        db: AsyncSession, req_data: CreateResponseSentenceRequest, user: User
):
    try:
        allowed_sentence_id = await current_sentence_crud.get_by_source_id(db, user.id, req_data.project_id)
        if not allowed_sentence_id or allowed_sentence_id.sentence_id != req_data.source_id:
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
            await current_sentence_crud.mark_as_replied(db, user.id, req_data.project_id)
            raise ConflictError(detail="Response already exist")

        response_sentence_obj = create_response_sentence_request_to_response_sentence(
            req_data, user.id
        )
        response = await response_sentence_crud.create(db, response_sentence_obj)
        await current_sentence_crud.mark_as_replied(db, user.id, req_data.project_id)
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
        ongoing_source = await current_sentence_crud.get_by_source_id(db, user.id, project_id)

        if ongoing_source:
            print("point 1 \n\n\n\n\n\n\n\n", ongoing_source.is_answered)
            # if not answered return current sentence.
            if not ongoing_source.is_answered:
                print("point 2 \n\n\n\n\n\n\n\n")
                source_sentence = await source_sentence_crud.get_by_id(db, ongoing_source.sentence_id)
                return source_sentence

            # if answered
            if ongoing_source.is_answered:
                print("point 3 \n\n\n\n\n\n\n\n")
                # generate next source id and store it
                next_id = await get_next_source_id(db, ongoing_source.sentence_id)
                if next_id:
                    print("point 4 \n\n\n\n\n\n\n\n")
                    await update_ongoing_sentence(db, user.id, project_id, next_id)
                    source_sentence = await source_sentence_crud.get_by_id(db, next_id)
                    return source_sentence

        # if not ongoing sentence id in database, check last response and find next source id
        last_response_id = await response_sentence_crud.get_last_source_id_by_user_id(
            db, user.id
        )
        print("point 5 \n\n\n\n\n\n\n\n")
        if last_response_id:  # if last response id exist
            next_id = await get_next_source_id(db, last_response_id.source_sentence_id)
            if next_id:
                print("point 6 \n\n\n\n\n\n\n\n")
                await update_ongoing_sentence(db, user.id, project_id, next_id)
                source_sentence = await source_sentence_crud.get_by_id(db, next_id)
                return source_sentence

        # if there are no responses, first sentence of the project will return
        first_sentence = await source_sentence_crud.get_first_of_project(db, project_id)
        print("sentence: ", first_sentence.source_sentence)
        if first_sentence:  # if first sentence exist save current sentence id in db and return sentence
            sentence_id = first_sentence.sentence_id
            print("point 7 \n\n\n\n\n\n\n\n")
            print(first_sentence)
            await update_ongoing_sentence(db, user.id, project_id, sentence_id)
            sentence = await source_sentence_crud.get_by_id(db, sentence_id)
            return sentence
        else:
            raise NotFoundError(detail="First sentence of project not found.")

    except Exception as e:
        print("execption 1\n\n\n\n\n\n\n\n")
        raise e
