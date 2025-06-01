from fastapi import APIRouter, HTTPException
from api.webhook.utils.dependencies import get_repo_instance
from api.schemas.response import UserResponse
from api.schemas.request import UserCreateRequest

user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    repo = get_repo_instance()
    user = await repo.users.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@user_router.post("/create", response_model=UserResponse)
async def create_user(data: UserCreateRequest):
    repo = get_repo_instance()
    user = await repo.users.create_user(
        user_id=data.user_id,
        full_name=data.full_name,
        is_premium=data.is_premium,
        username=data.username,
        referred_by=data.referred_by
    )
    return user


@user_router.get("/{user_id}/referrals", response_model=list[UserResponse])
async def get_user_referrals(user_id: int):
    repo = get_repo_instance()
    user = await repo.users.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    referrals = await repo.users.get_user_referrals(user_id)
    return referrals


@user_router.get("/", response_model=list[UserResponse])
async def get_all_users():
    repo = get_repo_instance()
    return await repo.users.get_all_users()
