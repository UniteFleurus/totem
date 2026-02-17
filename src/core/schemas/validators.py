import typing as t
from functools import singledispatch

from django.core import validators
from django.core.exceptions import ValidationError as DjangoValidationError
from pydantic import AfterValidator


def convert_validators(
    list_validators: t.List[t.Callable],
) -> t.Tuple[t.Dict, t.List[AfterValidator]]:
    finfos = {}
    fvalidators = []
    for validator in list_validators:
        extra_infos, extra_validator = convert_validator(validator)
        if extra_infos:
            finfos.update(extra_infos)
        if extra_validator:
            fvalidators.append(extra_validator)
    return finfos, fvalidators


def _wrap_django_validator(validator):
    """Wrap a django validator to a pydantic validator. The wrapper will catch
    the DjangoValidationError and raise a ValueError with the error message.
    """

    def wrapper(value):
        try:
            validator(value)
        except DjangoValidationError as e:
            raise ValueError(",".join(e.messages)) from e
        return value  # pyndatic validator must return the value, even if it is not modified

    return wrapper


def convert_validator(
    validator: t.Callable,
) -> t.Tuple[t.Dict, t.Union[AfterValidator, None]]:
    converted = convert_django_validator(validator)
    return converted


@singledispatch
def convert_django_validator(
    validator: t.Callable,  # pylint: disable=unused-argument
) -> t.Tuple[t.Dict, t.Union[AfterValidator, None]]:
    return {}, AfterValidator(_wrap_django_validator(validator))


@convert_django_validator.register(validators.RegexValidator)
def convert_django_regexvalidator(
    validator: t.Callable,
) -> t.Tuple[t.Dict, t.Union[AfterValidator, None]]:
    return {"pattern": validator.regex}, None


@convert_django_validator.register(validators.MinValueValidator)
def convert_django_minvaluevalidator(
    validator: t.Callable,
) -> t.Tuple[t.Dict, t.Union[AfterValidator, None]]:
    return {"ge": validator.limit_value}, None


@convert_django_validator.register(validators.MaxValueValidator)
def convert_django_maxvaluevalidator(
    validator: t.Callable,
) -> t.Tuple[t.Dict, t.Union[AfterValidator, None]]:
    return {"le": validator.limit_value}, None


@convert_django_validator.register(validators.MinLengthValidator)
def convert_django_minlengthvalidator(
    validator: t.Callable,
) -> t.Tuple[t.Dict, t.Union[AfterValidator, None]]:
    return {"min_length": validator.limit_value}, None


@convert_django_validator.register(validators.MaxLengthValidator)
def convert_django_maxlengthvalidator(
    validator: t.Callable,
) -> t.Tuple[t.Dict, t.Union[AfterValidator, None]]:
    return {"max_length": validator.limit_value}, None


@convert_django_validator.register(validators.DecimalValidator)
def convert_django_decimalvalidator(
    validator: t.Callable,
) -> t.Tuple[t.Dict, t.Union[AfterValidator, None]]:
    return {
        "decimal_places": validator.decimal_places,
        "max_digits": validator.max_digits,
    }, None
