from typing import Type

from typing_extensions import Annotated
from pydantic import AfterValidator,TypeAdapter, UUID4

from .types import Slug


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
