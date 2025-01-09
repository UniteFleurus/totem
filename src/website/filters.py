from typing import Optional

from ninja import FilterSchema, Field

from core.schemas.fields import ListOfUUID, ListOfSlug

#----------------------------------------------------
# Website Page
#----------------------------------------------------

class PageFilterSchema(FilterSchema):
    title: Optional[str] = Field(None, q='title__icontains', title="Title", description="Search term in the title.")
    is_published: Optional[bool] = Field(None, title="Is the page published", description="Search published or not pages.")
    user: Optional[ListOfUUID] = Field(None, q='user__in', description="Search page belonging to given users. Comma separated list of user UUID.")

#----------------------------------------------------
# Website Menu
#----------------------------------------------------

class MenuFilterSchema(FilterSchema):
    name: Optional[str] = Field(None, q='name__icontains', title="Name", description="Search term in the name.")
    new_window: Optional[bool] = Field(None, title="The menu opens its target on a new web page.", description="Search open in a new window.")
    page_slug: Optional[ListOfSlug] = Field(None, q='page__slug__in', description="Search menu pointing to a page.")
    parent: Optional[ListOfUUID] = Field(None, q='parent__in', description="Search child menus. Comma separated list of parent menu UUID.")
