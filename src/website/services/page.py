import typing as t

from pydantic import BaseModel as PydanticModel

from core.services.mixins import GenericModelService
from user.models import User
from website.models import Page


class PageModelService(GenericModelService):

    queryset = Page.objects.all()

    def get_queryset(self, operation=None):
        queryset = super().get_queryset(operation=operation)
        if operation in [self.LIST, self.FIND_ONE]:
            queryset = queryset.prefetch_related('user')
        return queryset

    def _preprocess_create_values(self, schema: PydanticModel, exclude_unset=True, user: t.Optional[t.Type[User]] = None, **kwargs: t.Any):
        data = super()._preprocess_create_values(schema, user=user, exclude_unset=exclude_unset, **kwargs)
        if 'user' not in data and user:
            data['user'] = user
        return data
