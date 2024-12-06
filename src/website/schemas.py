from typing import Optional
from ninja import ModelSchema

from core.schemas import types
from user.schemas import UserDisplayNameSchema
from user.models import User
from website.models import Page

#----------------------------------------------------
# Website Page
#----------------------------------------------------

class PageDisplayNameSchema(ModelSchema):
    slug: types.Slug

    class Meta:
        model = Page
        fields = ['slug', 'title']


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


class PageCreateSchemaIn(ModelSchema):
    slug: types.Slug
    user: Optional[types.ManyToOne(User, only_fields=['pk', 'username'])] = None

    class Meta:
        model = Page
        fields = ['title', 'content', 'is_published']


class PageUpdateSchemaIn(ModelSchema):
    slug: types.Slug = None
    user: Optional[types.ManyToOne(User, only_fields=['pk', 'username'])] = None

    class Meta:
        model = Page
        fields = ['title', 'content', 'is_published']
        fields_optional = '__all__'
