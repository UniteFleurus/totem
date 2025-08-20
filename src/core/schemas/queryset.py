from django.db import models as django_models
from pydantic import GetJsonSchemaHandler, SerializationInfo
from pydantic_core import core_schema as cs
from pydantic.json_schema import JsonSchemaValue
from typing import Any, Callable, Dict, Generic, TypeVar, Union, List, Type
from typing_extensions import get_args
from uuid import UUID

from .registry import core_schema_from_django_field


T = TypeVar("T", bound=django_models.Model)


class QuerySet(Generic[T]):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: Any, handler: Callable[[Any], cs.CoreSchema]
    ) -> cs.CoreSchema:
        model_class = get_args(source)[0]

        # Refuse abstract model
        is_abstract = getattr(model_class._meta, "abstract", False)
        if is_abstract:
            raise ValueError(
                "Abstract models cannot be used as QuerySet fields directly."
            )

        # Input is List of PK

        def validate_from_pk_list(
            values: List[Any]
        ) -> django_models.QuerySet:
            # Order is NOT preserved here. Check https://github.com/bnznamco/django-structured-field/blob/master/structured/pydantic/fields/queryset.py#L37
            # if needed
            qs = model_class._default_manager.filter(pk__in=values)
            objects = list(qs)
            if len(objects) != len(values):
                raise ValueError("Some given values does not exists.")
            return qs

        pk_schema = core_schema_from_django_field(model_class._meta.pk)
        from_pk_list_schema = cs.chain_schema(
            [
                cs.list_schema(pk_schema),
                cs.no_info_plain_validator_function(validate_from_pk_list),
            ]
        )

        # Input is List of Model Instance

        def validate_from_model_list(
            values: List[django_models.Model],
        ) -> django_models.QuerySet:
            if any(not isinstance(v, model_class) for v in values):
                raise ValueError(f"Expected list of {model_class.__class__.__name__} instances.")
            return model_class._default_manager.filter(pk__in=[v.pk for v in values])

        from_model_list_schema = cs.chain_schema(
            [
                cs.list_schema(cs.is_instance_schema(model_class)),
                cs.no_info_plain_validator_function(validate_from_model_list),
            ]
        )

        return cs.json_or_python_schema(
            json_schema=cs.union_schema(
                [
                    from_pk_list_schema,
                    from_model_list_schema,
                ]
            ),
            python_schema=cs.union_schema(
                [
                    cs.is_instance_schema(django_models.QuerySet),
                    from_pk_list_schema,
                    from_model_list_schema,
                ]
            ),
            metadata={
                "queryset_model": model_class
            },
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: cs.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        model_class = _core_schema.get("metadata", {}).get("queryset_model")
        if model_class:
                pk_schema = core_schema_from_django_field(model_class._meta.pk)
                json_schema = handler(cs.list_schema(pk_schema))
        else:
            json_schema = handler(cs.list_schema(cs.any_schema()))
        return json_schema