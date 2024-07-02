import re

from pydantic import BaseModel, ValidationError, ValidationInfo, field_validator


class UserModel(BaseModel):
    ...
    username: str
    email: str

    #  if not re.match(r'^[a-zA-Z0-9]+$', v):

    @field_validator("username")
    def username_match(cls, v: str, info: ValidationInfo) -> str:
        if not re.match(r'^[a-zA-Z0-9]+$', v):
            raise ValueError("username do not match")
        return v

    @field_validator("email")
    def email_match(cls, v: str, info: ValidationInfo) -> str:
        if not re.match(r'^[\w.-]+@[a-zA-Z\d.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError("email do not match")
        return v


try:
    UserModel(username="abc!", email="abcdemail.com")
except ValidationError as err:
    print(err.json(indent=4))
