from typing import List

from ninja import FilterSchema, Schema

from core.api import BaseModelController, ListModelControllerMixin
from oauth.authentication import OAuthTokenAuthentication
from totem.api import api_v1
from user.models import UserRole
from user.schemas import UserRoleFilterSchema, UserRoleSchema
from user.security import TokenHasScopePermissionModelControllerMixin


class UserRoleController(
    TokenHasScopePermissionModelControllerMixin,
    ListModelControllerMixin,
    BaseModelController,
):
    api = api_v1
    model = UserRole

    path_prefix = "/user-roles/"
    auth = [OAuthTokenAuthentication()]
    permission_map = {
        "read": ["totem.userrole.read"],
    }

    list_response_schema: Schema = List[UserRoleSchema]
    list_filter_schema: FilterSchema = UserRoleFilterSchema
    list_ordering_fields = [
        "name",
        "id",
    ]
    list_ordering_default_fields = ["id"]
