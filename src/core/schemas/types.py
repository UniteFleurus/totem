# pylint: disable=unused-argument
import typing as t

from django.db.models import Model
from ninja.types import DictStrAny
from pydantic import BaseModel
from pydantic_core import core_schema


class ExtraFieldInfos(BaseModel):
    alias: t.Optional[str] = None
    title: t.Optional[str] = None
    description: t.Optional[str] = None
    pattern: t.Optional[str] = None
    gt: t.Optional[int] = None
    ge: t.Optional[int] = None
    lt: t.Optional[int] = None
    le: t.Optional[int] = None
    min_length: t.Optional[int] = None
    max_length: t.Optional[int] = None
    max_digits: t.Optional[int] = None


class AnyObject:
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: t.Any, handler: t.Callable[..., t.Any]
    ) -> t.Any:
        return core_schema.with_info_plain_validator_function(cls.validate)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, schema: t.Any, handler: t.Callable[..., t.Any]
    ) -> DictStrAny:
        return {"type": "object"}

    @classmethod
    def validate(cls, value: t.Any, _: t.Any) -> t.Any:
        return value


SchemaKey = t.Tuple[t.Type[Model], str, int, str, str, str, str]
