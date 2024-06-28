# app/routers/auth.py
from typing import Annotated

from fastapi import APIRouter, Depends, Security
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

import app.auth.auth_service as auth_service
from app.auth.auth_schema import Token
from app.config.database.postgres_config import get_db
from app.crud.user_crud import get_by_email
from app.model.db_model import User
from app.schema.request.request_schema import SignInRequest
from app.schema.response.response_schema_map import map_user_to_userdata

router = APIRouter()


@router.post("/create-user", status_code=201)
async def create_user(
        req_data: SignInRequest, db: AsyncSession = Depends(get_db)
):
    try:
        user = await auth_service.create_new_user(db, req_data)
        return map_user_to_userdata(user)
    except Exception as e:
        raise e


# @router.post("/login", status_code=200)
@router.post("/token", status_code=200)
async def login_for_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: AsyncSession = Depends(get_db),
) -> Token:
    try:
        token = await auth_service.login_user(db, form_data.username, form_data.password)
        return Token(access_token=token, token_type="bearer")
    except Exception as e:
        raise e


@router.post("/validate-token", status_code=200)
async def validate_token(current_user: User = Depends(auth_service.get_current_user)):
    return map_user_to_userdata(current_user)


@router.get("/current-user")
async def read_system_status(current_user: User = Depends(auth_service.get_current_user)):
    return map_user_to_userdata(current_user)


@router.get("/admin-token")
async def read_own_items(
        current_user: User = Security(auth_service.get_current_active_admin),
):
    return [{"item_id": "Foo", "owner": current_user.username}]


@router.get("/test")
async def test(db: AsyncSession = Depends(get_db)):
    user = await get_by_email(db, "anjuna@email.com")
    return user
