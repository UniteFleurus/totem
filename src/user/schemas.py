from typing import List, Literal, Optional
from typing_extensions import Annotated

from ninja import Field, ModelSchema
from pydantic import EmailStr, UUID4

from core.schemas import types
from user.models import User
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


class UserDetailSchema(ModelSchema):

    email: EmailStr
    user_type: choices.UserType

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'language', 'is_active', 'user_type', 'avatar']
        # TODO add roles


class UserCreateSchemaIn(ModelSchema):

    email: EmailStr
    user_type: choices.UserType
    language: types.Language = "fr"

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

