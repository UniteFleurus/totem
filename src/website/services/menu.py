
from core.services.mixins import GenericModelService
from website.models import Menu


class MenuModelService(GenericModelService):

    queryset = Menu.objects.all()

    def get_queryset(self, operation=None):
        queryset = super().get_queryset(operation=operation)
        if operation in [self.LIST, self.FIND_ONE]:
            queryset = queryset.prefetch_related('page')
            queryset = queryset.prefetch_related('parent')
        return queryset
