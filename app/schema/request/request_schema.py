import re

from pydantic import BaseModel, field_validator, ValidationInfo


# create user request schema
class UserReqBase(BaseModel):
    username: str
    email: str

    @field_validator("username")
    def username_match(cls, v: str, info: ValidationInfo) -> str:
        if not re.match(r"^[a-zA-Z0-9]+$", v):
            raise ValueError("username do not match")
        return v

    @field_validator("email")
    def email_match(cls, v: str, info: ValidationInfo) -> str:
        if not re.match(r"^[\w.-]+@[a-zA-Z\d.-]+\.[a-zA-Z]{2,}$", v):
            raise ValueError("email do not match")
        return v


class SignInRequest(UserReqBase):
    password: str


class LoginRequest(UserReqBase):
    pass


class CreateProjectRequest(BaseModel):
    project_name: str


class CreateResponseSentenceRequest(BaseModel):
    source_id: int
    project_id: int
    sentence: str
