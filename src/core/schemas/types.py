from dataclasses import dataclass
from typing import Any, List, Union
from typing_extensions import Annotated

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from ninja.orm.fields import TYPES
from pydantic_core import CoreSchema, core_schema
from pydantic import Field, GetCoreSchemaHandler

#-----------------------------------------
# Scalar
#-----------------------------------------

Slug = Annotated[str, Field(pattern=r"^[-a-zA-Z0-9_]+\z")]


#-----------------------------------------
# Relations
#-----------------------------------------

@dataclass(frozen=True)
class ManyToOne:

    model_class: models.Model
    slug_field: str = 'pk'
    only_fields: Union[None, List[str]] = None
    queryset: models.QuerySet = None

    def __get_pydantic_core_schema__(
        self, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:

        if self.slug_field == 'pk':
            model_field = self.model_class._meta.pk
        else:
            model_field = self.model_class._meta.get_field(self.slug_field)

        internal_type = model_field.get_internal_type()
        _type = TYPES.get(internal_type, int)

        return core_schema.no_info_after_validator_function(
            self.fetch_object, handler(_type)
        )

    def fetch_object(self, value: Any):
        queryset = self.queryset
        if not queryset:
            queryset = self.model_class._default_manager.all()

        if self.only_fields:
            queryset = queryset.only(*self.only_fields)

        try:
            result = queryset.get(**{self.slug_field: value})
        except ObjectDoesNotExist as exc:
            raise ValueError(f"No {queryset.model._meta.verbose_name.lower()} found.") from exc
        return result
