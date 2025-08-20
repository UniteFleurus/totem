
from typing import Any, Callable, Tuple, Type

from pydantic_core import core_schema
from django.db.models import Model
from ninja.types import DictStrAny


class AnyObject:
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: Any, handler: Callable[..., Any]
    ) -> Any:
        return core_schema.with_info_plain_validator_function(cls.validate)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, schema: Any, handler: Callable[..., Any]
    ) -> DictStrAny:
        return {"type": "object"}

    @classmethod
    def validate(cls, value: Any, _: Any) -> Any:
        return value

SchemaKey = Tuple[Type[Model], str, int, str, str, str, str]
