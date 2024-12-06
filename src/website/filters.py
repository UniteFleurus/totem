from typing import Optional

from pydantic import UUID4
from ninja import FilterSchema, Field, ModelSchema

from core.schemas.fields import ListOfUUID
from user.schemas import UserDisplayNameSchema
from website.models import Page

#----------------------------------------------------
# Website Page
#----------------------------------------------------

class PageFilterSchema(FilterSchema):
    title: Optional[str] = Field(None, q='title__icontains', title="Title", description="Search term in the title.")
    is_published: Optional[bool] = Field(None, title="Is the page published", description="Search published or not pages.")
    user: Optional[ListOfUUID] = Field(None, q='user__in', description="Search page belonging to given users. Comma separated list of user UUID.")
