from typing import Optional

from ninja import FilterSchema, ModelSchema, Schema
from pydantic import UUID4, Field

from core.schemas.factory import create_request_schema, create_response_schema
from website.models import Menu, Page

# ----------------------------------------------------
# User
# ----------------------------------------------------


class PageDisplayNameSchema(ModelSchema):
    id: int

    class Meta:
        model = Page
        fields = ["id", "title"]


MenuSchema = create_response_schema(
    Menu,
    fields=[
        "id",
        "name",
        "parent",
        "page",
    ],
    optional_fields="__all__",
    # custom_fields=[
    #     ("page", PageDisplayNameSchema, Field(description="yolo"))
    # ]
)

class NewMenuSchema(MenuSchema):
    page: PageDisplayNameSchema


# from website.models import Menu, Page
# from website.schemas import MenuSchema

# Menu.objects.all()

# menu = Menu.objects.filter(page__isnull=False)[0]

# MenuSchema.schema_json()

# r = MenuSchema.from_orm(menu)
# r.model_dump()


# UserCreateSchema = create_request_schema(
#     User,
#     fields=[
#         "username",
#         "last_name",
#         "first_name",
#         "email",
#         "user_type",
#         "language",
#         "avatar",
#         "roles",
#     ],
# )
# UserUpdateSchema = create_request_schema(
#     User,
#     fields=[
#         "username",
#         "last_name",
#         "first_name",
#         "email",
#         "user_type",
#         "language",
#         "avatar",
#         "roles",
#     ],
#     optional_fields="__all__",
# )

# UserProfileSchema = create_request_schema(
#     User,
#     fields=["id", "last_name", "first_name", "email", "language", "avatar"],
#     optional_fields="__all__",
# )
