from dataclasses import dataclass
from typing import Any, List, Literal, Union
from typing_extensions import Annotated

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.conf import settings
from ninja.orm.fields import TYPES
from pydantic_core import CoreSchema, core_schema
from pydantic import Field, GetCoreSchemaHandler

#-----------------------------------------
# Scalar
#-----------------------------------------

Slug = Annotated[str, Field(pattern=r"^[-a-zA-Z0-9_]+\z")]

Language = Literal[*[item[0] for item in settings.LANGUAGES]]

#-----------------------------------------
# Relations
#-----------------------------------------

@dataclass(frozen=True)
class ManyToOne:

    model_class: models.Model
    slug_field: str = 'pk'
    only_fields: Union[None, List[str]] = None
    queryset: models.QuerySet = None

    def __get_pydantic_core_schema__(
        self, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:

        if self.slug_field == 'pk':
            model_field = self.model_class._meta.pk
        else:
            model_field = self.model_class._meta.get_field(self.slug_field)

        internal_type = model_field.get_internal_type()
        _type = TYPES.get(internal_type, int)

        from_any_schema = core_schema.chain_schema(
            [
                handler(_type),
                core_schema.no_info_plain_validator_function(self.fetch_object),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_any_schema, #core_schema.no_info_plain_validator_function(self.fetch_object),
            python_schema=core_schema.no_info_after_validator_function(
                self.fetch_object, handler(_type)
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                self._identity
            ),
        )

    def _identity(self, instance):
        return instance

    def fetch_object(self, value: Any):
        queryset = self.queryset
        if not queryset:
            queryset = self.model_class._default_manager.all()

        if self.only_fields:
            queryset = queryset.only(*self.only_fields)

        try:
            result = queryset.get(**{self.slug_field: value})
        except ObjectDoesNotExist as exc:
            raise ValueError(f"No {queryset.model._meta.verbose_name.lower()} found.") from exc
        return result


@dataclass(frozen=True)
class ManyToManyFromSlug:

    model_class: models.Model
    slug_field: str = 'pk'
    only_fields: Union[None, List[str]] = None
    queryset: models.QuerySet = None

    def __get_pydantic_core_schema__(
        self, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        if self.slug_field == 'pk':
            model_field = self.model_class._meta.pk
        else:
            model_field = self.model_class._meta.get_field(self.slug_field)

        internal_type = model_field.get_internal_type()
        _type = TYPES.get(internal_type, int)

        from_any_schema = core_schema.chain_schema(
            [
                handler(_type),
                core_schema.no_info_plain_validator_function(self.fetch_object),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_any_schema, #core_schema.no_info_plain_validator_function(self.fetch_object),
            python_schema=core_schema.with_info_after_validator_function(
                self.fetch_object, core_schema.list_schema(handler(_type))
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                self._identity
            ),
        )

    def _identity(self, instance,*args, **kwargs):
        print('======== indestnant', instance, args, kwargs)
        return instance

    def fetch_object(self, value: List[Any], *args, **kwargs):
        print('============valala', value, args, kwargs)
        queryset = self.queryset
        if not queryset:
            queryset = self.model_class._default_manager.all()

        if self.only_fields:
            queryset = queryset.only(*self.only_fields)

        try:
            result = list(queryset.filter(**{f"{self.slug_field}__in": value}))
        except ObjectDoesNotExist as exc:
            raise ValueError(f"No {queryset.model._meta.verbose_name.lower()} found.") from exc

        if len(result) != len(value):
            raise ValueError(f"Some {queryset.model._meta.verbose_name.lower()} are not found.")
        return result



@dataclass(frozen=True)
class ManyToManyToSlug:

    model_class: models.Model
    slug_field: str = 'pk'
    only_fields: Union[None, List[str]] = None
    queryset: models.QuerySet = None

    def __get_pydantic_core_schema__(
        self, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        if self.slug_field == 'pk':
            model_field = self.model_class._meta.pk
        else:
            model_field = self.model_class._meta.get_field(self.slug_field)

        internal_type = model_field.get_internal_type()
        _type = TYPES.get(internal_type, int)

        from_any_schema = core_schema.chain_schema(
            [
                handler(_type),
                #core_schema.no_info_plain_validator_function(self._identity),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_any_schema, #core_schema.no_info_plain_validator_function(self.fetch_object),
            python_schema=core_schema.with_info_before_validator_function(
                self._identity, core_schema.list_schema(handler(_type))
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                self._identity
            ),
        )

    def _identity(self, values, *args, **kwargs):
        print('==========instannce', values, args, kwargs)
        result = []
        for item in values:
            if isinstance(item, models.Model):
                result.append(getattr(item, self.slug_field, None))
            else:
                result.append(item)
        return result

    def fetch_object(self, value: List[Any]):
        print('===========value',value)
        return ['caca']
        queryset = self.queryset
        if not queryset:
            queryset = self.model_class._default_manager.all()

        if self.only_fields:
            queryset = queryset.only(*self.only_fields)

        try:
            result = list(queryset.filter(**{f"{self.slug_field}__in": value}))
        except ObjectDoesNotExist as exc:
            raise ValueError(f"No {queryset.model._meta.verbose_name.lower()} found.") from exc

        if len(result) != len(value):
            raise ValueError(f"Some {queryset.model._meta.verbose_name.lower()} are not found.")
        return result
