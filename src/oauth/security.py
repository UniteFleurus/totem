import hashlib
from typing import TYPE_CHECKING

from asgiref.sync import sync_to_async
from django.db.models.query import prefetch_related_objects
from django.http import HttpRequest
from ninja_extra import permissions
from ninja_extra.security import AsyncHttpBearer

from oauth.models import AccessToken

if TYPE_CHECKING:
    from ninja_extra.controllers.base import ControllerBase  # pragma: no cover


#------------------------------------------------------
# Authentication
#------------------------------------------------------

class OAuthTokenBearer(AsyncHttpBearer):

    async def authenticate(self, request, token):
        token_checksum = hashlib.sha256(token.encode("utf-8")).hexdigest()
        token = await (
            AccessToken.objects.select_related("user")
            .filter(token_checksum=token_checksum)
            .afirst()
        )
        if token and token.user_id:
            await sync_to_async(prefetch_related_objects)([token.user], 'roles')
            request.user = token.user
        return token

#------------------------------------------------------
# Permissions
#------------------------------------------------------

class TokenHasScope(permissions.BasePermission):

    def __init__(self, permission: str) -> None:
        self._permission = permission

    def has_permission(self, request: HttpRequest, controller: "ControllerBase"):
        return request.auth.is_valid([self._permission])
