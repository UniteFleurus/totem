from typing import List, Optional

from ninja import FilterSchema
from pydantic import Field

from core.schemas.factory import create_response_schema
from user.models import UserRole

# ----------------------------------------------------
# UserRole
# ----------------------------------------------------


UserRoleSchema = create_response_schema(
    UserRole,
    fields=[
        "id",
        "name",
        "permissions",
        "rules",
    ],
    optional_fields="__all__",
)


class UserRoleFilterSchema(FilterSchema):
    id: Optional[List[str]] = Field(
        None,
        q="id__in",
        title="Id",
        description="Search extact ID.",
    )
    name: Optional[str] = Field(
        None,
        q="name",
        title="Name",
        description="Search extact name.",
    )

    search: Optional[str] = Field(
        None,
        q=["name__icontains"],
        title="Search Term",
        description="Search term in the name.",
    )
