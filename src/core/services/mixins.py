import typing as t

from asgiref.sync import sync_to_async
from django.db import transaction, IntegrityError
from django.db.models import Model, QuerySet
from django.core.exceptions import ValidationError as DjangoValidationError
from ninja import FilterSchema
from ninja_extra import ModelService
from ninja_extra.exceptions import NotFound, PermissionDenied, ValidationError
from ninja_extra.shortcuts import get_object_or_exception
from pydantic import BaseModel as PydanticModel, ValidationError as PydanticValidationError

from user.access_policy import apply_access_rules
from user.models import User


class GenericModelService(ModelService):

    queryset = None

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

    # List / Retrieve

    def search_read(self, filters: FilterSchema = None, user: t.Optional[t.Type[User]] = None, **kwargs: t.Any) -> QuerySet:
        queryset = self.get_queryset(self.LIST)
        queryset = apply_access_rules(queryset, 'read', user)
        if filters is not None:
            queryset = filters.filter(queryset)
        return queryset

    async def search_read_async(self, filters: FilterSchema = None, user: t.Optional[t.Type[User]] = None, **kwargs: t.Any) -> QuerySet:
        return await sync_to_async(self.search_read, thread_sensitive=True)(filters=filters, user=user, **kwargs)

    def read(self, lookup_value: t.Any, lookup_name: str = 'pk', user: t.Optional[t.Type[User]] = None, **kwargs: t.Any) -> t.Any:
        return self._read_by_lookup(lookup_value=lookup_value, lookup_name=lookup_name, user=user, **kwargs)

    async def read_async(self, lookup_value: t.Any, lookup_name: str = 'pk', user: t.Optional[t.Type[User]] = None, **kwargs: t.Any) -> t.Any:
        return await sync_to_async(self._read_by_lookup, thread_sensitive=True)(lookup_value=lookup_value, lookup_name=lookup_name, user=user)

    def _read_by_lookup(self, lookup_name: str, lookup_value: t.Any, user: t.Optional[t.Type[User]] = None, **kwargs: t.Any) -> t.Any:
        queryset = self.get_queryset(self.FIND_ONE)
        queryset = apply_access_rules_sync(queryset, 'read', user)

        obj = get_object_or_exception(
            klass=queryset, error_message=None, exception=NotFound, **{lookup_name: lookup_value}
        )
        return obj

    # Create

    def create(self, schema: PydanticModel, exclude_unset=True, user: t.Optional[t.Type[User]] = None, **kwargs: t.Any) -> t.Any:
        data = self._create_preprocess_values(schema, user=user, exclude_unset=exclude_unset, **kwargs)
        try:
            with transaction.atomic():
                return self._create(data)
        except IntegrityError as exc:
            integrity_msg = str(exc)
            for const in self.model._meta.constraints:
                if const.name in integrity_msg and const.violation_error_message:
                    raise ValidationError(dict(detail=[const.violation_error_message])) from exc
            raise ValidationError(dict(detail=["Creation failed."])) from exc
        except DjangoValidationError as exc:
            raise ValidationError(dict(detail=exc.messages)) from exc

    def _create_preprocess_values(self, schema: PydanticModel, exclude_unset=True, user: t.Optional[t.Type[User]] = None, **kwargs: t.Any):
        data = schema.model_dump(by_alias=False, exclude_unset=exclude_unset)
        data.update(kwargs)
        return data

    def _create(self, validated_data):
        # Remove many-to-many relationships from validated_data.
        # They are not valid arguments to the default `.create()` method,
        # as they require that the instance has already been saved.
        many_to_many = {}
        for f in self.model._meta.get_fields():
            if getattr(f, 'many_to_many', False) and (f.name in validated_data):
                many_to_many[f.name] = validated_data.pop(f.name)

        # Create the object
        queryset = self.get_queryset(self.CREATE)
        obj = queryset.create(**validated_data)

        # Check if the created obj is in the access rule scope
        if not queryset.filter(pk=obj.pk).exists():
            raise PermissionDenied(f"You are not allowed to create {queryset.model._meta.verbose_name}, due to access rules restriction.")

        # Save many-to-many relationships after the instance is created.
        if many_to_many:
            for field_name, value in many_to_many.items():
                field = getattr(obj, field_name)
                # as we are in a creation, we don't need to use `.set()` which costs more SQL queries
                field.add(*value)

        return obj

    # Update

    async def update_async(self, schema: PydanticModel, lookup_value: t.Any, lookup_name: str = 'pk', user: t.Optional[t.Type[User]] = None, **kwargs: t.Any) -> t.Any:
        return await sync_to_async(self.update, thread_sensitive=True)(schema, lookup_value=lookup_value, lookup_name=lookup_name, user=user, **kwargs)

    def update(self, schema: PydanticModel, lookup_value: t.Any, lookup_name: str = 'pk', user: t.Optional[t.Type[User]] = None, **kwargs: t.Any) -> t.Any:
        queryset = self.get_queryset(self.UPDATE)
        queryset = apply_access_rules_sync(queryset, 'update', user)

        obj = get_object_or_exception(
            klass=queryset, error_message=None, exception=NotFound, **{lookup_name: lookup_value}
        )
        data = self._update_preprocess_values(obj, schema=schema, **kwargs)

        try:
            with transaction.atomic():
                return self._update(obj, data)
        except IntegrityError as exc:
            integrity_msg = str(exc)
            for const in self.model._meta.constraints:
                if const.name in integrity_msg and const.violation_error_message:
                    raise ValidationError(dict(detail=[const.violation_error_message])) from exc
            raise ValidationError(dict(detail=["Update failed."])) from exc
        except DjangoValidationError as exc:
            raise ValidationError(dict(detail=exc.messages)) from exc

    def _update_preprocess_values(self, instance, schema: PydanticModel, user: t.Optional[t.Type[User]] = None, **kwargs: t.Any):
        data = schema.model_dump(by_alias=True, exclude_unset=True) # context with instance ?
        data.update(kwargs)
        return data

    def _update(self, instance, validated_data):
        # Remove many-to-many relationships from validated_data.
        # They are not valid arguments to the default `.create()` method,
        # as they require that the instance has already been saved.
        many_to_many = {}
        for f in self.model._meta.get_fields():
            if getattr(f, 'many_to_many', False) and (f.name in validated_data):
                many_to_many[f.name] = validated_data.pop(f.name)

        # Do the update
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save(update_fields=list(validated_data))

        # Save many-to-many relationships after the instance is created.
        if many_to_many:
            for field_name, value in many_to_many.items():
                field = getattr(instance, field_name)
                field.set(value)
        return instance

    # Delete

    def delete(self, lookup_value: t.Any, lookup_name: str = 'pk', user: t.Optional[t.Type[User]] = None) -> t.Any:
        queryset = self.get_queryset(self.DELETE)
        queryset = apply_access_rules_sync(queryset, 'delete', user)

        obj = get_object_or_exception(
            klass=queryset, error_message=None, exception=NotFound, **{lookup_name: lookup_value}
        )
        try:
            with transaction.atomic():
                return self._delete(obj)
        except IntegrityError as exc:
            integrity_msg = str(exc)
            for const in self.model._meta.constraints:
                if const.name in integrity_msg and const.violation_error_message:
                    raise ValidationError(dict(detail=[const.violation_error_message])) from exc
            raise ValidationError(dict(detail=["Update failed."])) from exc

    async def delete_async(self, lookup_value: t.Any, lookup_name: str = 'pk', user: t.Optional[t.Type[User]] = None) -> t.Any:
        return await sync_to_async(self.delete, thread_sensitive=True)(lookup_value=lookup_value, lookup_name=lookup_name, user=user)

    def _delete(self, instance):
        return instance.delete()
