from typing_extensions import Annotated
from pydantic import UUID4
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.schemas import PaginationNumberPage, PaginationNumberParams
from app.user.services import UserService
from app.user.schemas import UserCreate, UserUpdate, UserInDB, UserParams


router = APIRouter(
    prefix="/api/v1/users",
    tags=["Users"],
)

def get_user_service():
    return UserService()

@router.post("/", response_model=UserInDB)
async def create_user(user: UserCreate, user_service: UserService = Depends(get_user_service)):
    return await user_service.create_user(user)

@router.get("/{user_id}", response_model=UserInDB)
async def get_user(user_id: UUID4, user_service: UserService = Depends(get_user_service)):
    user = await user_service.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserInDB)
async def update_user(user_id: UUID4, user: UserUpdate, user_service: UserService = Depends(get_user_service)):
    updated_user = await user_service.update_user(user_id, user)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@router.delete("/{user_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: UUID4, user_service: UserService = Depends(get_user_service)):
    await user_service.delete(user_id)
    return None

@router.get("/", response_model=PaginationNumberPage[UserInDB])
async def list_users(filters: Annotated[UserParams, Depends(UserParams)], pagination: Annotated[PaginationNumberParams, Depends(PaginationNumberParams)], user_service: UserService = Depends(get_user_service)):
    qs = await user_service.list(filters=filters)
    return await pagination.paginate(qs)
