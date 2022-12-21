from starlette import status
from app.schemas import TokenBase, User
import schemas as users
import utils as users_utils
from app.utils import get_current_user
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()


@router.get("/")
async def health_check():
    return {"Hello": "World"}


@router.post("/auth", response_model=TokenBase)
async def auth(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await users_utils.get_user_by_email(email=form_data.username)

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    if not users_utils.validate_password(
        password=form_data.password, hashed_password=user["hashed_password"]
    ):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    return await users_utils.create_user_token(user_id=user["id"])


@router.post("/sign-up", response_model=User)
async def create_user(user: users.UserCreate):
    db_user = await users_utils.get_user_by_email(email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await users_utils.create_user(user=user)


@router.get("/users/me", response_model=users.UserBase)
async def read_users_me(current_user: users.User = Depends(get_current_user)):
    return current_user


@router.post("/dweets", response_model=users.DweetDetailsModel, status_code=201)
async def create_dweet(dweet: DweetModel, current_user: User = Depends(get_current_user)):
    dweet = await dweet_utils.create_dweet(dweet, current_user)
    return dweet


@router.get("/dweets")
async def get_dweets(page: int = 1):
    total_cout = await dweet_utils.get_dweets_count()
    dweets = await dweet_utils.get_dweets(page)
    return {"total_count": total_cout, "results": dweets}


@router.get("/dweet/{dweet_id}", response_model=DweetDetailsModel)
async def get_dweet(post_id: int):
    return await dweet_utils.get_post(post_id)


@router.put("/dweet/{dweet_id}", response_model=DweetDetailsModel)
async def update_dweet(
    post_id: int, post_data: Dweet, current_user=Depends(get_current_user)
):
    post = await utils.get_dweet(dweet_id)
    if post["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to modify this post",
        )

    await utils.update_dweet(post_id=post_id, post=post_data)
    return await dweet_utils.get_post(post_id)
