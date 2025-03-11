from functools import reduce
from operator import and_, or_
from typing import Any, TypeVar, cast
from typing_extensions import Literal
from pydantic import BaseModel, ConfigDict
from pydantic.fields import FieldInfo

from tortoise.expressions import Q
from tortoise.models import Model, QuerySet


DEFAULT_IGNORE_NONE = True
DEFAULT_CLASS_LEVEL_EXPRESSION_CONNECTOR = "AND"
DEFAULT_FIELD_LEVEL_EXPRESSION_CONNECTOR = "OR"

LOGICAL_OPERATOR_MAP = {
    "OR": or_,
    "AND": and_,
}

T = TypeVar("T", bound=QuerySet)


class FilterSchema(BaseModel):

    model_config = ConfigDict(
        extra='ignore',
        ignore_none=DEFAULT_IGNORE_NONE,
        expression_connector=DEFAULT_CLASS_LEVEL_EXPRESSION_CONNECTOR
    )

    def custom_expression(self) -> Q:
        """
        Implement this method to return a combination of filters that will be used
        """
        raise NotImplementedError

    def get_filter_expression(self) -> Q:
        """
        Returns a Q expression based on the current filters
        """
        try:
            return self.custom_expression()
        except NotImplementedError:
            return self._connect_fields()

    def filter(self, queryset: T) -> T:
        return queryset.filter(self.get_filter_expression())

    def _resolve_field_expression(
        self, field_name: str, field_value: Any, field: FieldInfo
    ) -> Q:
        func = getattr(self, f"filter_{field_name}", None)
        if callable(func):
            return func(field_value)  # type: ignore[no-any-return]

        field_extra = field.json_schema_extra or {}

        q_expression = field_extra.get("q", None)  # type: ignore
        if not q_expression:
            return Q(**{field_name: field_value})
        elif isinstance(q_expression, str):
            if q_expression.startswith("__"):
                q_expression = f"{field_name}{q_expression}"
            return Q(**{q_expression: field_value})
        elif isinstance(q_expression, list):
            expression_connector = field_extra.get(  # type: ignore
                "expression_connector", DEFAULT_FIELD_LEVEL_EXPRESSION_CONNECTOR
            )
            q = Q()
            for q_expression_part in q_expression:
                q_expression_part = str(q_expression_part)
                if q_expression_part.startswith("__"):
                    q_expression_part = f"{field_name}{q_expression_part}"
                q = reduce(LOGICAL_OPERATOR_MAP[expression_connector], [q, Q(**{q_expression_part: field_value})])
            return q
        else:
            raise Exception(
                f"Field {field_name} of {self.__class__.__name__} defines an invalid value under 'q' kwarg.\n"
                f"Define a 'q' kwarg as a string or a list of strings, each string corresponding to a database lookup you wish to filter against:\n"
                f"  {field_name}: {field.annotation} = Field(..., q='<here>')\n"
                f"or\n"
                f"  {field_name}: {field.annotation} = Field(..., q=['lookup1', 'lookup2', ...])\n"
                f"You can omit the field name and make it implicit by starting the lookup directly by '__'."
                f"Alternatively, you can implement {self.__class__.__name__}.filter_{field_name} that must return a Q expression for that field"
            )

    def _connect_fields(self) -> Q:
        q = Q()
        for field_name, field in self.model_fields.items():
            filter_value = getattr(self, field_name)
            field_extra = field.json_schema_extra or {}
            ignore_none = field_extra.get(  # type: ignore
                "ignore_none",
                self.model_config["ignore_none"],  # type: ignore
            )

            # Resolve q for a field even if we skip it due to None value
            # So that improperly configured fields are easier to detect
            field_q = self._resolve_field_expression(field_name, filter_value, field)
            if filter_value is None and ignore_none:
                continue
            q = reduce(LOGICAL_OPERATOR_MAP[self.model_config["expression_connector"]], [q, field_q])

        return q
