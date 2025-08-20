import datetime
from decimal import Decimal
import itertools
from typing import Any, Callable, Dict, Iterator, List, Optional, Set, Tuple, Type, TypeVar, Union, no_type_check, cast
from uuid import UUID

from django.db.models import Field as DjangoField
from django.db.models import ManyToManyRel, ManyToOneRel, Model, QuerySet
from pydantic import create_model as create_pydantic_model, IPvAnyAddress
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined, core_schema

from ninja.errors import ConfigError
from ninja.orm.fields import title_if_lower
from ninja.openapi.schema import OpenAPISchema
from ninja.schema import Schema

from .queryset import QuerySet
from .registry import TypeRegistry
from .types import AnyObject, SchemaKey

__all__ = ["SchemaFactory", "factory", "create_request_schema", "create_response_schema"]


TModel = TypeVar("TModel")


# @no_type_check
# def create_serialization_m2m_link_type(
#     queryset: QuerySet,
#     slug_field: str = 'pk',
#     only_fields: Union[None, List[str]] = None
# ) -> Type[TModel]:

#     class M2MLink(type_):  # type: ignore
#         @classmethod
#         def __get_pydantic_core_schema__(cls, source, handler):
#             return core_schema.with_info_plain_validator_function(cls._validate)

#         @classmethod
#         def __get_pydantic_json_schema__(cls, schema, handler):
#             json_type = {
#                 int: "integer",
#                 str: "string",
#                 float: "number",
#                 UUID: "string",
#             }[type_]
#             return {"type": json_type}

#         @classmethod
#         def _validate(cls, v: Any, _):
#             try:
#                 return v.pk  # when we output queryset - we have db instances
#             except AttributeError:
#                 return type_(v)  # when we read payloads we have primakey keys

#     return M2MLink



class SchemaFactory:

    def __init__(self, registry: TypeRegistry) -> None:
        self.schemas: Dict[SchemaKey, Type[Schema]] = {}
        self.schema_names: Set[str] = set()
        self.type_registry: TypeRegistry = registry

    # Serialization Flow

    def create_serialization_schema(
        self,
        model: Type[Model],
        *,
        name: str = "",
        depth: int = 0,
        fields: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None,
        optional_fields: Optional[List[str]] = None,
        custom_fields: Optional[List[Tuple[str, Any, Any]]] = None,
        base_class: Type[Schema] = Schema,
    ) -> Type[Schema]:
        name = name or model.__name__

        if fields and exclude:
            raise ConfigError("Only one of 'fields' or 'exclude' should be set.")

        key = self.get_key(
            model, name, depth, fields, exclude, optional_fields, custom_fields
        )
        if key in self.schemas:
            return self.schemas[key]

        model_fields_list = list(self._selected_model_fields(model, fields, exclude))
        if optional_fields:
            if optional_fields == "__all__":
                optional_fields = [f.name for f in model_fields_list]

        definitions = {}
        for fld in model_fields_list:
            python_type, field_info = self.get_serialization_schema_field(
                fld,
                depth=depth,
                optional=optional_fields and (fld.name in optional_fields),
            )
            definitions[fld.name] = (python_type, field_info)

        if custom_fields:
            for fld_name, python_type, field_info in custom_fields:
                # if not isinstance(field_info, FieldInfo):
                #     field_info = Field(field_info)
                definitions[fld_name] = (python_type, field_info)

        if name in self.schema_names:
            name = self._get_unique_name(name)

        schema: Type[Schema] = create_pydantic_model(
            name,
            __config__=None,
            __base__=base_class,
            __module__=base_class.__module__,
            __validators__={},
            **definitions,
        )  # type: ignore
        # __model_name: str,
        # *,
        # __config__: ConfigDict | None = None,
        # __base__: None = None,
        # __module__: str = __name__,
        # __validators__: dict[str, AnyClassMethod] | None = None,
        # __cls_kwargs__: dict[str, Any] | None = None,
        # **field_definitions: Any,
        self.schemas[key] = schema
        self.schema_names.add(name)
        return schema

    @no_type_check
    def get_serialization_schema_field(
        self, field: DjangoField, *, depth: int = 0, optional: bool = False
    ) -> Tuple:
        "Returns pydantic field from django's model field"
        alias = None
        default = ...
        default_factory = None
        description = None
        title = None
        max_length = None
        nullable = False
        python_type = None

        if field.is_relation:
            if depth > 0:
                return self.get_related_field_schema(field, depth=depth)

            if not field.concrete and field.auto_created or field.null or optional:
                default = None
                nullable = True

            alias = getattr(field, "get_attname", None) and field.get_attname()

            pk_type = self.type_registry.to_pydantic_type(field.related_model._meta.pk, int)
            if field.one_to_many or field.many_to_many:
                m2m_type = self.create_serialization_m2m_link_type(pk_type)
                python_type = List[m2m_type]  # type: ignore
            else:
                python_type = pk_type

        else:
            _f_name, _f_path, _f_pos, field_options = field.deconstruct()
            blank = field_options.get("blank", False)
            null = field_options.get("null", False)
            max_length = field_options.get("max_length")

            python_type = self.type_registry.to_pydantic_type(field)

            if field.primary_key or blank or null or optional:
                default = None
                nullable = True

            if field.has_default():
                if callable(field.default):
                    default_factory = field.default
                else:
                    default = field.default

        if default_factory:
            default = PydanticUndefined

        if nullable:
            python_type = Union[python_type, None]  # aka Optional in 3.7+

        description = field.help_text or None
        title = title_if_lower(field.verbose_name)

        return (
            python_type,
            FieldInfo(
                default=default,
                alias=alias,
                validation_alias=alias,
                serialization_alias=alias,
                default_factory=default_factory,
                title=title,
                description=description,
                max_length=max_length,
            ),
        )

    @no_type_check
    def get_related_field_schema(self, field: DjangoField, *, depth: int) -> Tuple[OpenAPISchema]:
        model = field.related_model
        schema = self.create_schema(model, depth=depth - 1)
        default = ...
        if not field.concrete and field.auto_created or field.null:
            default = None
        if isinstance(field, ManyToManyField):
            schema = List[schema]  # type: ignore

        return (
            schema,
            FieldInfo(
                default=default,
                description=field.help_text,
                title=title_if_lower(field.verbose_name),
            ),
        )

    @no_type_check
    def create_serialization_m2m_link_type(self, type_: Type[TModel]) -> Type[TModel]:
        json_type = self.type_registry.get_json_type(type_)

        class M2MLink(type_):  # type: ignore
            @classmethod
            def __get_pydantic_core_schema__(cls, source, handler):
                return core_schema.with_info_plain_validator_function(cls._validate)

            @classmethod
            def __get_pydantic_json_schema__(cls, schema, handler):
                return {"type": json_type}

            @classmethod
            def _validate(cls, v: Any, _):
                try:
                    return v.pk  # when we output queryset - we have db instances
                except AttributeError:
                    return type_(v)  # when we read payloads we have primakey keys

        return M2MLink

    # Deserialization Flow

    def create_deserialization_schema(
        self,
        model: Type[Model],
        *,
        name: str = "",
        depth: int = 0,
        fields: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None,
        optional_fields: Optional[List[str]] = None,
        custom_fields: Optional[List[Tuple[str, Any, Any]]] = None,
        base_class: Type[Schema] = Schema,
    ) -> Type[Schema]:
        name = name or model.__name__

        if fields and exclude:
            raise ConfigError("Only one of 'fields' or 'exclude' should be set.")

        key = self.get_key(
            model, name, depth, fields, exclude, optional_fields, custom_fields
        )
        if key in self.schemas:
            return self.schemas[key]

        model_fields_list = list(self._selected_model_fields(model, fields, exclude))
        if optional_fields:
            if optional_fields == "__all__":
                optional_fields = [f.name for f in model_fields_list]

        definitions = {}
        for fld in model_fields_list:
            python_type, field_info = self.get_deserialization_schema_field(
                fld,
                depth=depth,
                optional=optional_fields and (fld.name in optional_fields),
            )
            definitions[fld.name] = (python_type, field_info)

        if custom_fields:
            for fld_name, python_type, field_info in custom_fields:
                # if not isinstance(field_info, FieldInfo):
                #     field_info = Field(field_info)
                definitions[fld_name] = (python_type, field_info)

        if name in self.schema_names:
            name = self._get_unique_name(name)

        schema: Type[Schema] = create_pydantic_model(
            name,
            __config__=None,
            __base__=base_class,
            __module__=base_class.__module__,
            __validators__={},
            **definitions,
        )  # type: ignore
        # __model_name: str,
        # *,
        # __config__: ConfigDict | None = None,
        # __base__: None = None,
        # __module__: str = __name__,
        # __validators__: dict[str, AnyClassMethod] | None = None,
        # __cls_kwargs__: dict[str, Any] | None = None,
        # **field_definitions: Any,
        self.schemas[key] = schema
        self.schema_names.add(name)
        return schema

    @no_type_check
    def get_deserialization_schema_field(
        self, field: DjangoField, *, depth: int = 0, optional: bool = False
    ) -> Tuple:
        "Returns pydantic field from django's model field"
        alias = None
        default = ...
        default_factory = None
        description = None
        title = None
        max_length = None
        nullable = False
        python_type = None

        if field.is_relation:
            if not field.concrete and field.auto_created or field.null or optional:
                default = None
                nullable = True

            alias = getattr(field, "get_attname", None) and field.get_attname()

            pk_type = self.type_registry.to_pydantic_type(field.related_model._meta.pk, int)
            if field.one_to_many or field.many_to_many:
                python_type = self.create_deserialization_m2m_link_type(field.related_model)
            else:
                python_type = pk_type

        else:
            _f_name, _f_path, _f_pos, field_options = field.deconstruct()
            blank = field_options.get("blank", False)
            null = field_options.get("null", False)
            max_length = field_options.get("max_length")

            python_type = self.type_registry.to_pydantic_type(field)

            if field.primary_key or blank or null:
                default = None
                nullable = True

            if field.has_default():
                if callable(field.default):
                    default_factory = field.default
                else:
                    default = field.default

        if default_factory:
            default = PydanticUndefined

        if nullable:
            python_type = Optional[python_type]

        # optional means not required in the payload. None
        # can be given in payload value but must be refused
        # if it is not a valid value.
        if optional:
            default=None
            default_factory=None

        description = field.help_text or None
        title = title_if_lower(field.verbose_name)

        # print('====================', title, field)
        # print("default=",default, bool(default))
        # print("default_factory=",default_factory)
        # print("nullable=",nullable)
        # print(python_type)

        return (
            python_type,
            FieldInfo(
                default=default,
                alias=alias,
                validation_alias=alias,
                serialization_alias=alias,
                default_factory=default_factory,
                title=title,
                description=description,
                max_length=max_length,
            ),
        )

    @no_type_check
    def create_deserialization_m2m_link_type(self, model_class: TModel) -> QuerySet[TModel]:
        qs_class = QuerySet[model_class]
        return qs_class

    # Utils and Common

    def get_key(
        self,
        model: Type[Model],
        name: str,
        depth: int,
        fields: Union[str, List[str], None],
        exclude: Optional[List[str]],
        optional_fields: Optional[Union[List[str], str]],
        custom_fields: Optional[List[Tuple[str, str, Any]]],
    ) -> SchemaKey:
        "returns a hashable value for all given parameters"
        # TODO: must be a test that compares all kwargs from init to get_key
        return (
            model,
            name,
            depth,
            str(fields),
            str(exclude),
            str(optional_fields),
            str(custom_fields),
        )

    def _get_unique_name(self, name: str) -> str:
        "Returns a unique name by adding counter suffix"
        for num in itertools.count(start=2):  # pragma: no branch
            result = f"{name}{num}"
            if result not in self.schema_names:
                break
        return result

    def _selected_model_fields(
        self,
        model: Type[Model],
        fields: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None,
    ) -> Iterator[DjangoField]:
        "Returns iterator for model fields based on `exclude` or `fields` arguments"
        all_fields = {f.name: f for f in self._model_fields(model)}

        if not fields and not exclude:
            for f in all_fields.values():
                yield f

        invalid_fields = (set(fields or []) | set(exclude or [])) - all_fields.keys()
        if invalid_fields:
            raise ConfigError(
                f"DjangoField(s) {invalid_fields} are not in model {model}"
            )

        if fields:
            for name in fields:
                yield all_fields[name]
        if exclude:
            for f in all_fields.values():
                if f.name not in exclude:
                    yield f

    def _model_fields(self, model: Type[Model]) -> Iterator[DjangoField]:
        "returns iterator with all the fields that can be part of schema"
        for fld in model._meta.get_fields():
            if isinstance(fld, (ManyToOneRel, ManyToManyRel)):
                # skipping relations
                continue
            yield cast(DjangoField, fld)

factory = SchemaFactory(TypeRegistry())

create_schema = factory.create_serialization_schema
create_response_schema = factory.create_serialization_schema
create_request_schema = factory.create_deserialization_schema
