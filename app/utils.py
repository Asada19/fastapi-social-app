import hashlib
import random
import string
from datetime import datetime, timedelta
from sqlalchemy import and_
from models.database import database
from users import tokens_table, users_table
from schemas import users as user_schema
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth")


def get_random_string(length=12):
    return "".join(random.choice(string.ascii_letters) for _ in range(length))


def hash_password(password: str, salt: str = None):
    if salt is None:
        salt = get_random_string()
    enc = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return enc.hex()


def validate_password(password: str, hashed_password: str):
    salt, hashed = hashed_password.split("$")
    return hash_password(password, salt) == hashed


async def get_user_by_email(email: str):
    query = users_table.select().where(users_table.c.email == email)
    return await database.fetch_one(query)


async def get_user_by_token(token: str):
    query = tokens_table.join(users_table).select().where(
        and_(
            tokens_table.c.token == token,
            tokens_table.c.expires > datetime.now()
        )
    )
    return await database.fetch_one(query)


async def create_user_token(user_id: int):
    query = (
        tokens_table.insert()
        .values(expires=datetime.now() + timedelta(weeks=2), user_id=user_id)
        .returning(tokens_table.c.token, tokens_table.c.expires)
    )

    return await database.fetch_one(query)


async def create_user(user: user_schema.UserCreate):
    salt = get_random_string()
    hashed_password = hash_password(user.password, salt)
    query = users_table.insert().values(
        email=user.email, name=user.name, hashed_password=f"{salt}${hashed_password}"
    )
    user_id = await database.execute(query)
    token = await create_user_token(user_id)
    token_dict = {"token": token["token"], "expires": token["expires"]}

    return {**user.dict(), "id": user_id, "is_active": True, "token": token_dict}


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = await get_user_by_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return user