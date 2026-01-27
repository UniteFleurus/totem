# pylint: disable=protected-access,unused-argument
from typing import Any, Callable, List, Optional, TypeVar, Union

from django.core.exceptions import ObjectDoesNotExist
from django.db import models as django_models
from pydantic import GetJsonSchemaHandler, SerializationInfo, TypeAdapter
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema as cs

T = TypeVar("T", bound=django_models.Model)

# This file provides pydantic field for Django model relations, including ForeignKey and ManyToManyField.
# https://docs.pydantic.dev/latest/concepts/json_schema/#implementing-__get_pydantic_core_schema__


def _get_lookup_field_instance(model_class, lookup_field):
    """Return the django model field instance for the given lookup field name.
    :param model_class: the django model class
    :param lookup_field: the lookup field name, can be "pk" for primary key
    """
    lookup_fname = lookup_field
    if lookup_field == "pk":
        lookup_fname = model_class._meta.pk.name
    return model_class._meta.get_field(lookup_fname)


def _get_lookup_field_type_adapter(model_class, lookup_field):
    # avoid circular dependency
    from .fields import convert_db_field  # pylint: disable=wrong-import-position

    python_type, dummy = convert_db_field(
        _get_lookup_field_instance(model_class, lookup_field)
    )
    return TypeAdapter(python_type)


# ----------------------------------------------------------------
# Many-to-One (ForeignKey)
# ----------------------------------------------------------------


def create_foreignkey_field(model_class, optional: bool, lookup_fname: str = None):
    lookup_fname = lookup_fname or "pk"  # force not None

    class CustomForeignKey(ForeignKey):
        model = model_class
        lookup_field = lookup_fname

    if optional:
        return Optional[CustomForeignKey]
    return CustomForeignKey


class ForeignKey:

    model: django_models.QuerySet
    lookup_field: str = "pk"
    only_fields: Union[None, List[str]] = None

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: Callable[[Any], cs.CoreSchema],
    ) -> cs.CoreSchema:
        lookup_type_adapter = _get_lookup_field_type_adapter(
            cls.model, cls.lookup_field
        )

        pk_schema = lookup_type_adapter.core_schema

        # Input is PK (or slug field)

        def validate_from_pk(value: Any) -> django_models.Model:
            queryset = cls.model.objects.all()  # TODO allow customizing queryset
            try:
                result = queryset.get(**{cls.lookup_field: value})
            except ObjectDoesNotExist as exc:
                raise ValueError(
                    f"No {queryset.model._meta.verbose_name.lower()} found."
                ) from exc
            return result

        pk_schema = lookup_type_adapter.core_schema
        from_pk_schema = cs.chain_schema(
            [
                pk_schema,
                cs.no_info_plain_validator_function(validate_from_pk),
            ]
        )

        def serialize_data(
            instance: django_models.Model,
            info: SerializationInfo,  # pylint: disable=unused-argument
        ) -> List[Any]:
            return getattr(instance, cls.lookup_field)

        return cs.json_or_python_schema(
            json_schema=cs.union_schema(
                [
                    from_pk_schema,
                ]
            ),
            python_schema=cs.union_schema(
                [
                    cs.is_instance_schema(django_models.Model),
                    from_pk_schema,
                ]
            ),
            serialization=cs.plain_serializer_function_ser_schema(
                serialize_data, info_arg=True
            ),
        )


# ----------------------------------------------------------------
# Many-to-Many (Queryset)
# ----------------------------------------------------------------

def create_queryset_field(model_class, optional: bool, lookup_fname: str = None):

    lookup_fname = lookup_fname or "pk"  # force not None

    class QuerySetFieldLink(QuerySetField):
        model = model_class
        lookup_field = lookup_fname

    if optional:
        return Optional[QuerySetFieldLink]
    return QuerySetFieldLink


class QuerySetField:

    model: T = None
    lookup_field: str = "pk"

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source: Any,
        handler: Callable[[Any], cs.CoreSchema],
    ) -> cs.CoreSchema:
        model_class = cls.model
        lookup_field = _get_lookup_field_instance(model_class, cls.lookup_field)

        # Refuse abstract model
        is_abstract = getattr(model_class._meta, "abstract", False)
        if is_abstract:
            raise ValueError(
                "Abstract models cannot be used as QuerySet fields directly."
            )

        # Input is List of PK

        def validate_from_pk_list(values: List[Any]) -> django_models.QuerySet:
            # Order is NOT preserved here. Check https://github.com/bnznamco/django-structured-field/blob/master/structured/pydantic/fields/queryset.py#L37
            # if needed
            q_expr = django_models.Q(**{f"{lookup_field.name}__in": values})
            qs = model_class._default_manager.filter(q_expr)
            objects = list(qs)
            if len(objects) != len(values):
                raise ValueError("Some given values does not exists.")
            return qs

        lookup_type_adapter = _get_lookup_field_type_adapter(
            cls.model, cls.lookup_field
        )

        pk_schema = lookup_type_adapter.core_schema
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
            if any(
                not isinstance(v, model_class) for v in values
            ):  # pylint: disable=W1116
                raise ValueError(
                    f"Expected list of {model_class.__class__.__name__} instances."
                )
            q_expr = django_models.Q(
                **{
                    f"{lookup_field.name}__in": [
                        getattr(v, lookup_field.name) for v in values
                    ]
                }
            )
            return model_class._default_manager.filter(q_expr)

        from_model_list_schema = cs.chain_schema(
            [
                cs.list_schema(cs.is_instance_schema(model_class)),
                cs.no_info_plain_validator_function(validate_from_model_list),
            ]
        )

        def serialize_data(
            qs: django_models.QuerySet,
            info: SerializationInfo,  # pylint: disable=unused-argument
        ) -> List[Any]:
            return [getattr(item, lookup_field.name) for item in qs]

        return cs.json_or_python_schema(
            json_schema=cs.union_schema(
                [
                    from_model_list_schema,
                    from_pk_list_schema,
                ]
            ),
            python_schema=cs.union_schema(
                [
                    cs.is_instance_schema(django_models.QuerySet),
                    from_model_list_schema,
                    from_pk_list_schema,
                ]
            ),
            serialization=cs.plain_serializer_function_ser_schema(
                serialize_data, info_arg=True
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: cs.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        model_class = cls.model

        if model_class:
            pk_schema = _get_lookup_field_type_adapter(
                cls.model, cls.lookup_field
            ).core_schema
            json_schema = handler(cs.list_schema(pk_schema))
        else:
            json_schema = handler(cs.list_schema(cs.any_schema()))
        return json_schema
