from pydantic import BaseModel


class User(BaseModel):
    id: int
    username: int


class Profile(BaseModel):
    user: User()
