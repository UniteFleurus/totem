import typing as t

from pydantic import BaseModel as PydanticModel

from core.services.mixins import GenericModelService
from user.models import User


class UserModelService(GenericModelService):

    queryset = User.objects.all()

    async def read_my_profile(self, user: t.Optional[t.Type[User]]) -> User:
        perms = set()
        for r in user.roles.all():
            perms |= set(r.permissions)
        user.permissions = list(perms)
        return user

