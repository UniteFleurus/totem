import inspect
from abc import ABC, abstractmethod
from functools import wraps
from operator import attrgetter, itemgetter
from typing import (
    Any,
    Callable,
    List,
    Optional,
    Tuple,
    Type,
    Union,
)

from django.db.models import QuerySet
from django.http import HttpRequest
from ninja import P, Query, Schema
from ninja.constants import NOT_SET
from ninja.utils import (
    contribute_operation_args,
    is_async_callable,
)
from pydantic import BaseModel


__all__ = [
    "OrderingBase",
    "Ordering",
    "ordering",
]


class OrderingBase(ABC):
    class Input(Schema): ...

    InputSource = Query(...)

    def __init__(self, *, pass_parameter: Optional[str] = None, **kwargs: Any) -> None:
        self.pass_parameter = pass_parameter

    @abstractmethod
    def ordering_queryset(
        self, items: Union[QuerySet, List], ordering_input: Any
    ) -> Union[QuerySet, List]: ...


class Ordering(OrderingBase):
    class Input(Schema):
        pass  # do not display `ordering` as parameter if ordering_fields is not set

    def __init__(
        self,
        ordering_fields: Optional[List[str]] = None,
        pass_parameter: Optional[str] = None,
        default_ordering_fields: Optional[List[str]] = ["id"]
    ) -> None:
        super().__init__(pass_parameter=pass_parameter)
        self.ordering_fields = ordering_fields or "__all__"
        self.default_ordering_fields = default_ordering_fields or "__all__"
        self.Input = self.create_input(ordering_fields, default_ordering_fields)  # type:ignore

    def create_input(self, ordering_fields: Optional[List[str]], default_ordering_fields: Optional[List[str]]) -> Type[Input]:
        if ordering_fields:
            choices = [f"`{word}`" for word in set(default_ordering_fields) | set(ordering_fields)]
            description = f"Possible values are {', '.join(choices)}"

            class DynamicInput(Ordering.Input):
                ordering: Query[Optional[str], P(default=",".join(default_ordering_fields or ordering_fields), description=description)]  # type:ignore[type-arg,valid-type]

            return DynamicInput
        return Ordering.Input

    def ordering_queryset(
        self, items: Union[QuerySet, List], ordering_input: Input
    ) -> Union[QuerySet, List]:
        ordering_ = self.get_ordering(items, ordering_input.ordering)
        if ordering_:
            if isinstance(items, QuerySet):
                return items.order_by(*ordering_)
            elif isinstance(items, list) and items:

                def multisort(xs: List, specs: List[Tuple[str, bool]]) -> List:
                    orerator = itemgetter if isinstance(xs[0], dict) else attrgetter
                    for key, reverse in reversed(specs):
                        xs.sort(key=orerator(key), reverse=reverse)
                    return xs

                return multisort(
                    items,
                    [
                        (o[int(o.startswith("-")) :], o.startswith("-"))
                        for o in ordering_
                    ],
                )
        return items

    def get_ordering(
        self, items: Union[QuerySet, List], value: Optional[str]
    ) -> List[str]:
        if value:
            fields = [param.strip() for param in value.split(",")]
            return self.remove_invalid_fields(items, fields)
        return []

    def remove_invalid_fields(
        self, items: Union[QuerySet, List], fields: List[str]
    ) -> List[str]:
        valid_fields = list(self.get_valid_fields(items))

        def term_valid(term: str) -> bool:
            if term.startswith("-"):
                term = term[1:]
            return term in valid_fields

        return [term for term in fields if term_valid(term)]

    def get_valid_fields(self, items: Union[QuerySet, List]) -> List[str]:
        valid_fields: List[str] = []
        if self.ordering_fields == "__all__":
            if isinstance(items, QuerySet):
                valid_fields = self.get_all_valid_fields_from_queryset(items)
            elif isinstance(items, list):
                valid_fields = self.get_all_valid_fields_from_list(items)
        else:
            valid_fields = list(self.ordering_fields)
            if self.default_ordering_fields:
                valid_fields += [fname[1:] if fname.startswith("-") else fname for fname in self.default_ordering_fields]
        return valid_fields

    def get_all_valid_fields_from_queryset(self, items: QuerySet) -> List[str]:
        return [str(field.name) for field in items.model._meta.fields] + [
            str(key) for key in items.query.annotations
        ]

    def get_all_valid_fields_from_list(self, items: List) -> List[str]:
        if not items:
            return []
        item = items[0]
        if isinstance(item, BaseModel):
            return list(item.model_fields.keys())
        if isinstance(item, dict):
            return list(item.keys())
        if hasattr(item, "_meta") and hasattr(item._meta, "fields"):
            return [str(field.name) for field in item._meta.fields]
        return []


def ordering(func_or_pgn_class: Any = NOT_SET, **orderator_params: Any) -> Callable:
    """
    @api.get(...
    @ordering
    def my_view(request):

    or

    @api.get(...
    @ordering(OrderingCustom)
    def my_view(request):

    """

    isfunction = inspect.isfunction(func_or_pgn_class)
    isnotset = func_or_pgn_class == NOT_SET

    ordering_class: Type[Union[OrderingBase, OrderingBase]] = Ordering # default value

    if isfunction:
        return _inject_ordering(func_or_pgn_class, ordering_class)

    if not isnotset:
        ordering_class = func_or_pgn_class

    def wrapper(func: Callable) -> Any:
        return _inject_ordering(func, ordering_class, **orderator_params)

    return wrapper


def _inject_ordering(
    func: Callable,
    ordering_class: Type[Union[OrderingBase]],
    **orderator_params: Any,
) -> Callable:
    orderator = ordering_class(**orderator_params)
    if is_async_callable(func):

        @wraps(func)
        async def view_with_ordering(request: HttpRequest, **kwargs: Any) -> Any:
            ordering_params = kwargs.pop("ninja_ordering")
            if orderator.pass_parameter:
                kwargs[orderator.pass_parameter] = ordering_params

            items = await func(request, **kwargs)

            result = await orderator.ordering_queryset(
                items, ordering_input=ordering_params
            )
            return result

    else:

        @wraps(func)
        def view_with_ordering(request: HttpRequest, **kwargs: Any) -> Any:
            ordering_params = kwargs.pop("ninja_ordering")
            if orderator.pass_parameter:
                kwargs[orderator.pass_parameter] = ordering_params

            items = func(request, **kwargs)

            result = orderator.ordering_queryset(
                items, ordering_input=ordering_params
            )
            return result

    contribute_operation_args(
        view_with_ordering,
        "ninja_ordering",
        orderator.Input,
        orderator.InputSource,
    )

    return view_with_ordering
