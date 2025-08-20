import datetime
from decimal import Decimal
from enum import Enum
import inspect
from typing import Dict, List, Literal
from pydantic import IPvAnyAddress, EmailStr
from pydantic_core import core_schema as cs
from uuid import UUID

from django.contrib.postgres import fields as psql_fields
from django.db.models import fields
from .types import AnyObject


def core_schema_from_django_field(field):
    # TODO: handle enum/choices, max_lenght and other constraints of django db field
    # to integrate them into schema.
    choices = getattr(field, "choices", None)
    if choices:
        return Enum(field.name, choices)

    python_type = TypeRegistry().to_pydantic_type(field, default=str)
    core_schema_method = {
        int: "int_schema",
        str: "str_schema",
        UUID: "uuid_schema",
    }.get(python_type, "any_schema")
    return getattr(cs, core_schema_method)()


class ClassLookupDict:
    """
    Takes a dictionary with classes as keys.
    Lookups against this object will traverses the object's inheritance
    hierarchy in method resolution order, and returns the first matching value
    from the dictionary or raises a KeyError if nothing matches.
    Note: this is copy/paste from DRF
    """
    def __init__(self, mapping):
        self.mapping = mapping

    def __getitem__(self, key):
        base_class = key.__class__
        for cls in inspect.getmro(base_class):
            if cls in self.mapping:
                return self.mapping[cls]
        raise KeyError('Class %s not found in lookup.' % base_class.__name__)

    def __setitem__(self, key, value):
        self.mapping[key] = value


class TypeRegistry(object):

    # Default

    field_map = ClassLookupDict({
        fields.AutoField: int,
        fields.BigAutoField: int,
        fields.BigIntegerField: int,
        fields.BinaryField: bytes,
        fields.BooleanField: bool,
        fields.CharField: str,
        fields.EmailField: EmailStr,
        fields.DateField: datetime.date,
        fields.DateTimeField: datetime.datetime,
        fields.DecimalField: Decimal,
        fields.DurationField: datetime.timedelta,
        # fields.FileField: str,
        fields.FilePathField: str,
        fields.FloatField: float,
        fields.GenericIPAddressField: IPvAnyAddress,
        fields.IPAddressField: IPvAnyAddress,
        fields.IntegerField: int,
        fields.NullBooleanField: bool,
        fields.PositiveBigIntegerField: int,
        fields.PositiveIntegerField: int,
        fields.PositiveSmallIntegerField: int,
        fields.SlugField: str,
        fields.SmallAutoField: int,
        fields.SmallIntegerField: int,
        fields.TextField: str,
        fields.TimeField: datetime.time,
        fields.UUIDField: UUID,
        # postgres fields:
        psql_fields.JSONField: AnyObject,
        psql_fields.ArrayField: List,
        psql_fields.CICharField: str,
        psql_fields.CIEmailField: str,
        psql_fields.CITextField: str,
        psql_fields.HStoreField: Dict,
    })

    json_type = {
        int: "integer",
        str: "string",
        float: "number",
        UUID: "string",
    }

    # Singleton

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance

    # Methods

    def to_pydantic_type(self, django_field, default=None):
        choices = getattr(django_field, "choices", None)
        if choices:
            return Literal[*[item[0] for item in choices]]
        try:
            return self.field_map[django_field]
        except KeyError:
            if default:
                return default
            return str

    def get_json_type(self, python_type, default=None):
        return self.json_type.get(python_type, default)
