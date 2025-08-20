from typing import List, Literal, Optional
from typing_extensions import Annotated

from ninja.orm import create_schema
from ninja import ModelSchema
from pydantic import EmailStr, Field, UUID4

from core.schemas.factory import create_request_schema, create_response_schema
from core.schemas.queryset import QuerySet
from user.models import User, UserRole
from user import choices


class UserDisplayNameSchema(ModelSchema):
    id: UUID4

    class Meta:
        model = User
        fields = ['id', 'username']


UserSchema = create_response_schema(User, fields=["id", "username", "last_name", "first_name", "email", "user_type", "language", "is_active", "avatar", "roles"], optional_fields="__all__")
UserCreateSchema = create_request_schema(User, fields=["username", "password", "last_name", "first_name", "email", "user_type", "language", "avatar", "roles"])
UserUpdateSchema = create_request_schema(User, fields=["username", "password", "last_name", "first_name", "email", "user_type", "language", "avatar", "roles"], optional_fields="__all__")


# class UserCreateSchema(ModelSchema):

#     roles: QuerySet[UserRole]
#     # roles = Annotated[ManyToManyFromSlug(UserRole.objects.all()), Field(title="caca")]

#     class Meta:
#         model = User
#         fields = ["username", "password", "last_name", "first_name", "email", "user_type", "language", "avatar", "roles"]


