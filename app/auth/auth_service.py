import os
from datetime import datetime, timedelta, timezone
from typing import Union

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import (
    SecurityScopes,
)
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

import app.crud.user_crud as user_crud
from app.auth.auth_schema import TokenData, Token
from app.config.database.postgres_config import get_db
from app.exception import ConflictError
from app.model.db_enum import UserRole
from app.model.db_model import User as UserModel
from app.schema.request.request_schema import SignInRequest
from app.schema.request.request_schema_map import sign_in_req_to_user

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def create_new_user(db: AsyncSession, request_data: SignInRequest):
    try:
        user_by_username = await user_crud.get_by_username(db, request_data.username)
        if user_by_username:
            raise ConflictError(detail="Username already exist!")

        user_by_email = await user_crud.get_by_email(db, request_data.email)
        if user_by_email:
            raise ConflictError(detail="Email already in use!")

        request_data.password = get_password_hash(request_data.password)
        user_model_data = sign_in_req_to_user(request_data)
        user_model_data.scopes = UserRole.USER

        user = await user_crud.create_user(db, user_model_data)
        return user

    except Exception as e:
        raise e


async def login_user(db: AsyncSession, username: str, password: str):
    try:
        user = await authenticate_user(db, username, password)
        if not user:
            raise HTTPException(status_code=400, detail="Incorrect username or password")
        access_token_expires = timedelta(
            minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
        )
        print("\n\n\n\n\n\n\n\n\n user role", user.scopes)
        access_token = create_access_token(
            data={"sub": user.username, "scopes": [str(user.scopes)], "email": user.email},
            expires_delta=access_token_expires,
        )
        return access_token
    except Exception as e:
        raise e


async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await user_crud.get_by_email(db, username)
    if not isinstance(user, UserModel):
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def get_current_user(
        security_scopes: SecurityScopes,
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db),
):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(
            token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")]
        )
        print(payload)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (InvalidTokenError, ValidationError):
        raise credentials_exception

    user = await user_crud.get_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception

    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )

    return user


async def get_current_active_admin(
        current_user: UserModel = Security(get_current_user, scopes=["admin"])
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_active_user(
        current_user: UserModel = Security(get_current_user, scopes=["regular_user"])
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    print("to encode: ", to_encode)
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM")
    )
    return encoded_jwt
