from pydantic import BaseModel, Field


class UserOut(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    is_active: bool 


class UserRegister(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str
    is_active: bool = Field(default=True, nullable=True)


class Token(BaseModel):
    access_token: str
    token_type: str