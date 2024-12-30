from typing import Optional
from typing_extensions import Annotated

from ninja import Field, ModelSchema
from pydantic import UUID4

from core.schemas import types
from user.schemas import UserDisplayNameSchema
from user.models import User
from website.models import Menu, Page

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

#----------------------------------------------------
#  Website Menu
#----------------------------------------------------

class MenuDisplayNameSchema(ModelSchema):
    id: UUID4

    class Meta:
        model = Menu
        fields = ['id', 'name']


class MenuListSchema(ModelSchema):
    parent: MenuDisplayNameSchema|None = None
    page: PageDisplayNameSchema|None = None

    class Meta:
        model = Menu
        exclude = ['parent_path']


class MenuDetailSchema(ModelSchema):
    parent: MenuDisplayNameSchema|None = None
    page: PageDisplayNameSchema|None = None

    class Meta:
        model = Menu
        exclude = ['parent_path']


class MenuCreateSchemaIn(ModelSchema):
    parent: Optional[types.ManyToOne(Menu, only_fields=['pk', 'name'])] = None
    page: Optional[types.ManyToOne(Page, only_fields=['slug', 'title'], slug_field="slug")] = None

    class Meta:
        model = Menu
        exclude = ['id', 'parent_path', 'create_date']


class MenuUpdateSchemaIn(ModelSchema):
    parent: Optional[types.ManyToOne(Menu, only_fields=['pk', 'name'])] = None
    page: Optional[types.ManyToOne(Page, only_fields=['slug', 'title'], slug_field="slug")] = None

    class Meta:
        model = Menu
        exclude = ['id', 'parent_path', 'create_date']
        fields_optional = '__all__'
