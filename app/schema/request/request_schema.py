from pydantic import BaseModel


# create user request schema
class SignInRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str
