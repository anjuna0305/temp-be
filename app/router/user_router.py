from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import app.service.user_service as user_service
from app.auth.auth_service import get_current_active_user
from app.config.database.postgres_config import get_db
from app.model.db_model import User
from app.schema.request.request_schema import (
    CreateResponseSentenceRequest,
)

router = APIRouter()


@router.get("/test")
async def test(id: int, db: AsyncSession = Depends(get_db)):
    print("controller called **********\n\n\n\n\n")
    next_id = await user_service.get_next_source_id(db, id)
    return next_id


# @router.get("/source")
# async def get_source(source_id:int):


@router.get("/responses")
async def get_responses(
        project_id: int,
        skip: int = 0,
        limit: int = 20,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_active_user),
):
    try:
        results = await user_service.get_res_sentence_by_user_and_project_ids(
            db, user.id, project_id, limit, skip
        )
        return results
    except Exception as e:
        raise e


@router.post("/response/new")
async def get_responses(
        req_data: CreateResponseSentenceRequest,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_active_user),
):
    try:
        results = await user_service.create_new_response(db, req_data, user)
        return results
    except Exception as e:
        raise e


@router.get("/source")
async def get_source_sentence(
        project_id: int,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_active_user),
):
    try:
        results = await user_service.get_source_sentence(db, project_id, user)
        return results
    except Exception as e:
        raise e


@router.get("/source/{source_id}")
async def get_source_sentence(
        source_id: int,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_active_user),
):
    try:
        results = await user_service.get_sentence_by_id(db, source_id)
        return results
    except Exception as e:
        raise e

# @router.get("/source/current")
# async def get_current_source_sentence(
#         db: AsyncSession = Depends(get_db),
#         user: User = Depends(get_current_active_user),
# ):
#     try:
#         results = await source_sentence_service.get_by_id(db, sentence_id)
#         return results
#     except Exception as e:
#         raise e
