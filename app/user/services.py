from pydantic import UUID4
from typing import Optional

from app.core.security import get_password_hash, verify_password
from app.core.services.mixins import CRUDMixin
from app.user.models import User
from app.user.schemas import UserCreate, UserUpdate, UserInDB, UserParams


class UserService(CRUDMixin[User, UserCreate, UserUpdate, UserParams]):

    def __init__(self):
        super().__init__(User)

    async def create_user(self, user: UserCreate) -> UserInDB:
        print('===========', user)
        hashed_password = get_password_hash(user.password)
        user_dict = user.dict(exclude={"password"})
        user_dict["hashed_password"] = hashed_password
        user_obj = await self.model.create(**user_dict)
        return UserInDB(id=user_obj.id, username=user_obj.username, first_name=user_obj.first_name, last_name=user_obj.last_name, is_active=user_obj.is_active)

    async def update_user(self, user_id: UUID4, user: UserUpdate) -> Optional[UserInDB]:
        user_obj = await self.get(user_id)
        if not user_obj:
            return None
        update_data = user.dict(exclude_unset=True)
        if user.password:
            update_data['hashed_password'] = get_password_hash(user.password)
        await self.update(user_id, UserUpdate(**update_data))
        return UserInDB(id=user_obj.id, username=user_obj.username, first_name=user_obj.first_name, last_name=user_obj.last_name, is_active=user_obj.is_active)

    async def authenticate(self, username: str, password: str) -> Optional[UserInDB]:
        user = await self.get_user_by_username(username)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    async def get_user_by_username(self, username: str) -> Optional[UserInDB]:
        user = await User.get(username=username)
        if user:
            return UserInDB(id=user.id, username=user.username, first_name=user.first_name, last_name=user.last_name, is_active=user.is_active)
        return None
