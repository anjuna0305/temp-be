from app.model.db_enum import UserRole
from app.model.db_model import User
from app.schema.request.request_schema import SignInRequest


def sign_in_req_to_user(schema: SignInRequest) -> User:
    user: User = User(
        username=schema.username,
        email=schema.email,
        hashed_password=schema.password
    )
    return user
