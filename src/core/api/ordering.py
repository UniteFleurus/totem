from typing import (
    List,
    Optional,
    Type,
    Union
)
from ninja import Field, P, Query, Schema
from django.db.models import QuerySet
from ninja_extra.ordering import Ordering as NinjaOrdering


class Ordering(NinjaOrdering):

    def __init__(
        self,
        ordering_fields: Optional[List[str]] = None,
        default_fields: Optional[List[str]] = None,
        pass_parameter: Optional[str] = None,
    ) -> None:
        super().__init__(pass_parameter=pass_parameter)
        self.default_ordering_fields = default_fields or []
        if not ordering_fields:
            self.ordering_fields = "__all__"
        else:
            self.ordering_fields = self.default_ordering_fields + ordering_fields
        self.Input = self.create_input(default_fields)  # type:ignore

    def create_input(self, ordering_fields: Optional[List[str]]) -> Type[NinjaOrdering.Input]:
        if ordering_fields:

            class DynamicInput(Ordering.Input):
                ordering: Query[Optional[str], P(default=",".join(ordering_fields))] = Field(None, description="Comma separated list of field to use to sort output records.")  # type:ignore[type-arg,valid-type]

            return DynamicInput
        return Ordering.Input

    def ordering_queryset(
        self, items: Union[QuerySet, List], ordering_input: NinjaOrdering.Input
    ) -> Union[QuerySet, List]:
        # force the default order field if no one is given (even if `?ordering=` is passed empty)
        if not ordering_input.ordering:
            ordering_input = NinjaOrdering.Input(ordering=','.join(self.default_ordering_fields))
        return super().ordering_queryset(items, ordering_input)
