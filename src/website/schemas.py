from typing import Optional
from typing_extensions import Annotated

from pydantic import UUID4
from ninja import Field, ModelSchema

from core.schemas import RelationalModelSchemaMixin
from user.schemas import UserDisplayNameSchema
from website.models import Page

#----------------------------------------------------
# Website Page
#----------------------------------------------------

class PageListSchema(ModelSchema):
    user: UserDisplayNameSchema|None  = None
    url: str  # non-nullable property

    class Meta:
        model = Page
        exclude = ['id', 'content']


class PageDetailSchema(ModelSchema):
    user: UserDisplayNameSchema|None  = None
    url: str  # non-nullable property

    class Meta:
        model = Page
        exclude = ['id']


class PageCreateSchemaIn(RelationalModelSchemaMixin, ModelSchema):
    slug: str = Field(pattern=r"^[-a-zA-Z0-9_]+\z")
    user: Annotated[Optional[UUID4], Field(queryset_only_fields=['pk', 'username'])] = None

    class Meta:
        model = Page
        fields = ['title', 'slug', 'content', 'is_published']


class PageUpdateSchemaIn(RelationalModelSchemaMixin, ModelSchema):
    slug: Annotated[str, Field(pattern=r"^[-a-zA-Z0-9_]+\z")] = None  # --> correct one
    user: Optional[UUID4] = Field(None, queryset_only_fields=['pk', 'username'])

    class Meta:
        model = Page
        fields = ['title', 'user', 'content', 'is_published']
        fields_optional = '__all__'


class PageUpdateSchemaIn(RelationalModelSchemaMixin, ModelSchema):
    slug: Annotated[str, Field(pattern=r"^[-a-zA-Z0-9_]+\z")] = None  # --> correct one
    user: Optional[UUID4] = Field(None, queryset_only_fields=['pk', 'username'])

    class Meta:
        model = Page
        fields = ['title', 'user', 'content', 'is_published']
        fields_optional = '__all__'
