from typing import Optional

from ninja import FilterSchema, ModelSchema, Schema
from pydantic import UUID4, Field

from core.schemas.factory import create_request_schema, create_response_schema
from user.models import User

# ----------------------------------------------------
# User
# ----------------------------------------------------


class ProfilePathParam(Schema):
    id: UUID4


class UserDisplayNameSchema(ModelSchema):
    id: UUID4

    class Meta:
        model = User
        fields = ["id", "username"]


UserSchema = create_response_schema(
    User,
    fields=[
        "id",
        "username",
        "last_name",
        "first_name",
        "email",
        "is_active",
        "user_type",
        "language",
        "avatar",
        "roles",
    ],
    optional_fields="__all__",
)
UserCreateSchema = create_request_schema(
    User,
    fields=[
        "username",
        "last_name",
        "first_name",
        "email",
        "user_type",
        "language",
        "avatar",
        "roles",
    ],
)
UserUpdateSchema = create_request_schema(
    User,
    fields=[
        "username",
        "last_name",
        "first_name",
        "email",
        "user_type",
        "language",
        "avatar",
        "roles",
    ],
    optional_fields="__all__",
)

UserProfileSchema = create_request_schema(
    User,
    fields=["id", "last_name", "first_name", "email", "language", "avatar"],
    optional_fields="__all__",
)


class UserFilterSchema(FilterSchema):
    username: Optional[str] = Field(
        None,
        q="username__icontains",
        title="Username",
        description="Search term in the username.",
    )
    email: Optional[str] = Field(
        None,
        q="email__icontains",
        title="Email",
        description="Search term in the email.",
    )
    is_active: Optional[bool] = Field(
        None, title="Is the user activated.", description="Search active or not users."
    )

    search: Optional[str] = Field(
        None,
        q=["username__icontains", "email__icontains"],
        title="Search Term",
        description="Search term in the username or in the email.",
    )
