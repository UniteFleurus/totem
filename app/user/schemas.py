from typing import Optional
from pydantic import BaseModel, Field, UUID4

from app.core.schemas import FilterSchema, PaginationNumberParams


class UserBase(BaseModel):
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserCreate(UserBase):
    password: str  # Mot de passe en clair

class UserUpdate(UserBase):
    password: Optional[str] = None  # Mot de passe en clair

class UserInDB(UserBase):
    id: UUID4
    is_active: bool

    class Config:
        from_attributes = True


class UserParams(FilterSchema):
    is_active: Optional[bool] = Field(None, q=['is_active'])
    search: Optional[str] = Field(None, q=['username__icontains'])
