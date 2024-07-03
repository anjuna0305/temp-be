from typing import Annotated

from fastapi import APIRouter, Depends, Security
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

import app.auth.auth_service as auth_service
from app.auth.auth_schema import Token
from app.config.database.postgres_config import get_db
from app.crud.user_crud import get_by_email
from app.model.db_model import User
from app.schema.request.request_schema import (
    SignInRequest,
    CreateResponseSentenceRequest,
)
from app.schema.response.response_schema_map import map_user_to_userdata
import app.crud.source_sentence_crud as source_sentence_service
from app.auth.auth_service import get_current_active_user

import app.service.user_service as user_service
from app.exception import BadRequestError

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
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    try:
        results = await user_service.get_response_sentence_by_user_id(
            db, user.id, limit, skip
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
    sentence_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    try:
        results = await source_sentence_service.get_by_id(db, sentence_id)
        return results
    except Exception as e:
        raise e
