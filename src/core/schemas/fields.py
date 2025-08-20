from dataclasses import dataclass
from typing import Any, List, Literal, Type, Union
from typing_extensions import Annotated

# from django.core.exceptions import ObjectDoesNotExist
# from django.db import models
from django.conf import settings
from ninja.orm.fields import TYPES
# from pydantic_core import CoreSchema, core_schema
from pydantic import Field #, GetCoreSchemaHandler
from pydantic import AfterValidator,TypeAdapter, UUID4
from typing_extensions import Annotated


#-----------------------------------------
# Serialization (from internal value to representation )
#-----------------------------------------

Slug = Annotated[str, Field(pattern=r"^[-a-zA-Z0-9_]+\z")]

Language = Literal[*[item[0] for item in settings.LANGUAGES]]



def split_string_validator(class_type: Type, separator: str = ','):
    ta = TypeAdapter(class_type)

    def _split_list_of_string(value):
        if isinstance(value, str):
            result = []
            if value == "":
                return result

            value_list = value.split(separator)
            for item in value_list:
                # this line will raise a ValueError if item is not compliant.
                result.append(ta.validate_python(item))

            return result
        return value

    return _split_list_of_string


ListOfString = Annotated[str, AfterValidator(split_string_validator(class_type=str))]
ListOfUUID = Annotated[str, AfterValidator(split_string_validator(class_type=UUID4))]
ListOfInt = Annotated[str, AfterValidator(split_string_validator(class_type=int))]
ListOfSlug = Annotated[str, AfterValidator(split_string_validator(class_type=Slug))]