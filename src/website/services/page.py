import typing as t
from django.db.models import Model, QuerySet
from django.core.exceptions import ValidationError as DjangoValidationError
from ninja_extra import ModelService

from user.access_policy import apply_access_rules_sync
from user.models import User
from website.models import Page
from website.filters import PageFilterSchema


from asgiref.sync import sync_to_async
from pydantic import BaseModel as PydanticModel

from django.db import transaction, IntegrityError
from ninja_extra.exceptions import NotFound, PermissionDenied, ValidationError
from ninja_extra.shortcuts import get_object_or_exception



class GenericModelService(ModelService):

    queryset = Page.objects.all()

    LIST = 'list'
    FIND_ONE = 'find_one'
    CREATE = 'create'
    UPDATE = 'update'
    DELETE = 'delete'

    def __init__(self, model: t.Optional[t.Type[Model]] = None) -> None:
        if model is None:
            model = self.queryset.model
        super().__init__(model)

    def get_queryset(self, operation=None):
        return self.model.objects.all()

    # Get All / Get One

    def get_all(self, filters: PageFilterSchema = None, user: t.Optional[t.Type[User]] = None, **kwargs: t.Any) -> QuerySet:
        queryset = self.get_queryset(self.LIST)
        queryset = apply_access_rules_sync(queryset, 'read', user)
        if filters is not None:
            queryset = filters.filter(queryset)
        return queryset

    def get_one(self, lookup_value: t.Any, lookup_name: str = 'pk', user: t.Optional[t.Type[User]] = None, **kwargs: t.Any) -> t.Any:
        return self._get_one_by_lookup(lookup_value=lookup_value, lookup_name=lookup_name, user=user, **kwargs)

    async def get_one_async(self, lookup_value: t.Any, lookup_name: str = 'pk', user: t.Optional[t.Type[User]] = None, **kwargs: t.Any) -> t.Any:
        return await sync_to_async(self._get_one_by_lookup, thread_sensitive=True)(lookup_value=lookup_value, lookup_name=lookup_name, user=user)

    def _get_one_by_lookup(self, lookup_name: str, lookup_value: t.Any, user: t.Optional[t.Type[User]] = None, **kwargs: t.Any) -> t.Any:
        queryset = self.get_queryset(self.FIND_ONE)
        queryset = apply_access_rules_sync(queryset, 'read', user)

        obj = get_object_or_exception(
            klass=self.model, error_message=None, exception=NotFound, **{lookup_name: lookup_value}
        )
        return obj

    # Create

    def create(self, schema: PydanticModel, exclude_unset=True, user: t.Optional[t.Type[User]] = None, **kwargs: t.Any) -> t.Any:
        data = self._preprocess_create_values(schema, user=user, exclude_unset=exclude_unset, **kwargs)
        try:
            with transaction.atomic():
                return self._perform_create(data)
        except IntegrityError as exc:
            integrity_msg = str(exc)
            for const in self.model._meta.constraints:
                if const.name in integrity_msg and const.violation_error_message:
                    raise ValidationError(dict(detail=[const.violation_error_message])) from exc
            raise ValidationError(dict(detail=["Creation failed."])) from exc
        except DjangoValidationError as exc:
            raise ValidationError(dict(detail=exc.messages)) from exc

    def _preprocess_create_values(self, schema: PydanticModel, exclude_unset=True, user: t.Optional[t.Type[User]] = None, **kwargs: t.Any):
        data = schema.model_dump(by_alias=False, exclude_unset=exclude_unset)

        data.update(kwargs)
        return data

    def _perform_create(self, values):
        queryset = self.get_queryset(self.CREATE)
        # create the object
        obj = queryset.create(**values)
        # check if the created obj is in the access rule scope
        if not queryset.filter(pk=obj.pk).exists():
            raise PermissionDenied(f"You are not allowed to create {queryset.model._meta.verbose_name}, due to access rules restriction.")
        return obj

    # Update

    async def update_async(self, schema: PydanticModel, lookup_value: t.Any, lookup_name: str = 'pk', user: t.Optional[t.Type[User]] = None, **kwargs: t.Any) -> t.Any:
        return await sync_to_async(self.update, thread_sensitive=True)(schema, lookup_value=lookup_value, lookup_name=lookup_name, user=user, **kwargs)

    def update(self, schema: PydanticModel, lookup_value: t.Any, lookup_name: str = 'pk', user: t.Optional[t.Type[User]] = None, **kwargs: t.Any) -> t.Any:
        queryset = self.get_queryset(self.UPDATE)
        queryset = apply_access_rules_sync(queryset, 'update', user)

        obj = get_object_or_exception(
            klass=self.model, error_message=None, exception=NotFound, **{lookup_name: lookup_value}
        )
        return self._perform_update(obj, schema, **kwargs)

    def _perform_update(self, instance, schema: PydanticModel, **kwargs: t.Any):
        # TODO : handle m2m fields
        data = schema.model_dump(by_alias=True, exclude_unset=True)
        data.update(kwargs)

        for attr, value in data.items():
            setattr(instance, attr, value)
        instance.save(update_fields=list(data))
        return instance

    # Delete

    def delete(self, lookup_value: t.Any, lookup_name: str = 'pk', user: t.Optional[t.Type[User]] = None) -> t.Any:
        queryset = self.get_queryset(self.DELETE)
        queryset = apply_access_rules_sync(queryset, 'delete', user)

        obj = get_object_or_exception(
            klass=self.model, error_message=None, exception=NotFound, **{lookup_name: lookup_value}
        )
        self._perform_delete(obj)

    async def delete_async(self, lookup_value: t.Any, lookup_name: str = 'pk', user: t.Optional[t.Type[User]] = None) -> t.Any:
        return await sync_to_async(self.delete, thread_sensitive=True)(lookup_value=lookup_value, lookup_name=lookup_name, user=user)

    def _perform_delete(self, instance):
        return instance.delete()


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
