from typing import List, Literal, Optional
from typing_extensions import Annotated

from ninja import Field, ModelSchema
from pydantic import EmailStr, UUID4

from core.schemas import types
from user.models import User, UserRole
from user import choices


class UserDisplayNameSchema(ModelSchema):
    id: UUID4

    class Meta:
        model = User
        fields = ['id', 'username']

#----------------------------------------------------
# User
#----------------------------------------------------

class UserListSchema(ModelSchema):

    email: EmailStr
    user_type: choices.UserType

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'language', 'is_active', 'user_type', 'avatar']

from pydantic import BaseModel, ConfigDict, field_serializer, model_serializer
from typing import Any

class UserDetailSchema(ModelSchema):

    email: EmailStr
    user_type: choices.UserType
    roles: types.ManyToManyToSlug(UserRole, only_fields=['pk', 'name'])
    #roles: List[str] = None

    # @field_serializer('roles')
    # def serialize_dt(self, val: Any, _info):
    #     print('===========val',val)
    #     return val

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'language', 'is_active', 'user_type', 'avatar']
        # TODO add roles



class UserCreateSchemaIn(ModelSchema):

    email: EmailStr
    user_type: choices.UserType
    language: types.Language = "fr"
    roles: types.ManyToManyFromSlug(UserRole, only_fields=['pk', 'name'])

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'language', 'is_active', 'user_type']
        # TODO add roles + validation


class UserUpdateSchemaIn(ModelSchema):

    email: EmailStr = None
    user_type: choices.UserType = None
    language: types.Language = None

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'language', 'is_active', 'user_type']
        fields_optional = '__all__'
        # TODO add roles + validation




class UserProfileSchemaOut(ModelSchema):

    email: EmailStr
    user_type: choices.UserType
    permissions: List[str] = []

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'language', 'user_type', 'avatar']
        # TODO add roles

