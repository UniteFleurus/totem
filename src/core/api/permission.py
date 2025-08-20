"""
Copied from DRF and ninja extra
Provides a set of pluggable permission policies.
"""

from abc import ABC, ABCMeta, abstractmethod
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, Generic, List, Tuple, Type, TypeVar, Union

from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from ninja.constants import NOT_SET
from ninja.types import DictStrAny
from ninja.utils import (
    contribute_operation_args,
    is_async_callable,
)

# from core.api.controllers import BaseController


SAFE_METHODS = ("GET", "HEAD", "OPTIONS")

T = TypeVar("T")


class OperationHolderMixin:
    def __and__(  # type:ignore[misc]
        self: Union[Type["BasePermission"], "BasePermission"],
        other: Union[Type["BasePermission"], "BasePermission"],
    ) -> "OperandHolder[AND]":
        return OperandHolder(AND, self, other)

    def __or__(  # type:ignore[misc]
        self: Union[Type["BasePermission"], "BasePermission"],
        other: Union[Type["BasePermission"], "BasePermission"],
    ) -> "OperandHolder[OR]":
        return OperandHolder(OR, self, other)

    def __rand__(  # type:ignore[misc]
        self: Union[Type["BasePermission"], "BasePermission"],
        other: Union[Type["BasePermission"], "BasePermission"],
    ) -> "OperandHolder[AND]":  # pragma: no cover
        return OperandHolder(AND, other, self)

    def __ror__(  # type:ignore[misc]
        self: Union[Type["BasePermission"], "BasePermission"],
        other: Union[Type["BasePermission"], "BasePermission"],
    ) -> "OperandHolder[OR]":  # pragma: no cover
        return OperandHolder(OR, other, self)

    def __invert__(  # type:ignore[misc]
        self: Union[Type["BasePermission"], "BasePermission"],
    ) -> "SingleOperandHolder[NOT]":
        return SingleOperandHolder(NOT, self)


class BasePermissionMetaclass(OperationHolderMixin, ABCMeta):
    ...


class BasePermission(ABC, metaclass=BasePermissionMetaclass):  # pragma: no cover
    """
    A base class from which all permission classes should inherit.
    """

    message: Any = "You do not have permission to perform this action."

    @abstractmethod
    def has_permission(
        self, request: HttpRequest
    ) -> bool:
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return True

    def has_object_permission(
        self, request: HttpRequest, obj: Any
    ) -> bool:
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return True


class SingleOperandHolder(OperationHolderMixin, Generic[T]):
    def __init__(
        self,
        operator_class: Type[BasePermission],
        op1_class: Union[Type["BasePermission"], "BasePermission"],
    ) -> None:
        super().__init__()
        self.operator_class = operator_class
        self.op1_class = op1_class

    def __call__(self, *args: Tuple[Any], **kwargs: DictStrAny) -> BasePermission:
        op1 = self.op1_class
        if isinstance(self.op1_class, (type, OperationHolderMixin)):
            op1 = self.op1_class()
        return self.operator_class(op1)  # type: ignore


class OperandHolder(OperationHolderMixin, Generic[T]):
    def __init__(
        self,
        operator_class: Type["BasePermission"],
        op1_class: Union[Type["BasePermission"], "BasePermission"],
        op2_class: Union[Type["BasePermission"], "BasePermission"],
    ) -> None:
        self.operator_class = operator_class
        # Instance the Permission class before using it
        self.op1 = op1_class
        self.op2 = op2_class
        self.message = op1_class.message
        if isinstance(op1_class, (type, OperationHolderMixin)):
            self.op1 = op1_class()

        if isinstance(op2_class, (type, OperationHolderMixin)):
            self.op2 = op2_class()

    def __call__(self, *args: Tuple[Any], **kwargs: DictStrAny) -> BasePermission:
        return self.operator_class(self.op1, self.op2)  # type: ignore


class AND(BasePermission):
    def __init__(self, op1: "BasePermission", op2: "BasePermission") -> None:
        self.op1 = op1
        self.op2 = op2
        self.message = op1.message

    def has_permission(
        self, request: HttpRequest
    ) -> bool:
        if self.op1.has_permission(request):
            self.message = self.op2.message
            return self.op2.has_permission(request)
        return False

    def has_object_permission(
        self, request: HttpRequest, obj: Any
    ) -> bool:
        return self.op1.has_object_permission(
            request, obj
        ) and self.op2.has_object_permission(request, obj)


class OR(BasePermission):
    def __init__(self, op1: "BasePermission", op2: "BasePermission") -> None:
        self.op1 = op1
        self.op2 = op2
        self.message = op1.message

    def has_permission(
        self, request: HttpRequest
    ) -> bool:
        if not self.op1.has_permission(request):
            self.message = self.op2.message
            return self.op2.has_permission(request)
        return True

    def has_object_permission(
        self, request: HttpRequest, obj: Any
    ) -> bool:
        return self.op1.has_object_permission(
            request, obj
        ) or self.op2.has_object_permission(request, obj)


class NOT(BasePermission):
    def __init__(self, op1: "BasePermission") -> None:
        self.op1 = op1
        self.message = op1.message

    def has_permission(
        self, request: HttpRequest
    ) -> bool:
        return not self.op1.has_permission(request)

    def has_object_permission(
        self, request: HttpRequest, obj: Any
    ) -> bool:
        return not self.op1.has_object_permission(request, obj)


def evaluate_permissions(request: HttpRequest, permissions: List[OperationHolderMixin]):
    for permission_class in permissions:
        permission_instance = permission_class
        if isinstance(permission_class, (type, OperationHolderMixin)):
            permission_instance = permission_class()  # type: ignore[operator]

        if not permission_instance.has_permission(request):
            message = getattr(permission_instance, "message", "You don't have the right to do this operation.")
            raise PermissionDenied(message)


#----------------------------------------------------
# Permission Decorator
#----------------------------------------------------

def check_permissions(permissions: List[OperationHolderMixin]) -> Callable:
    """
    @api.get(...
    @check_permissions
    def my_view(request):

    or

    @api.get(...
    @check_permissions(OrderingCustom)
    def my_view(request):

    """
    def wrapper(func: Callable) -> Any:
        return _inject_permissions_check(func, permissions)

    return wrapper


def _inject_permissions_check(
    func: Callable,
    permissions: List[OperationHolderMixin],
) -> Callable:

    if is_async_callable(func):

        @wraps(func)
        async def view_with_permission_check(request: HttpRequest, **kwargs: Any) -> Any:
            evaluate_permissions(request, permissions)
            return await func(request, **kwargs)

    else:

        @wraps(func)
        def view_with_permission_check(request: HttpRequest, **kwargs: Any) -> Any:
            evaluate_permissions(request, permissions)
            return func(request, **kwargs)

    return view_with_permission_check
