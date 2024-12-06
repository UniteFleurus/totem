from typing import Type

from typing_extensions import Annotated
from pydantic import AfterValidator, UUID4


def split_string_validator(class_type: Type, separator: str = ','):

    def _split_list_of_string(value):
        if isinstance(value, str):
            result = []
            if value == "":
                return result

            value_list = value.split(separator)
            for item in value_list:
                # this line will raise a ValueError if item is not compliant.
                result.append(class_type(item))
            return result
        return value

    return _split_list_of_string


ListOfString = Annotated[str, AfterValidator(split_string_validator(class_type=str))]
ListOfUUID = Annotated[str, AfterValidator(split_string_validator(class_type=UUID4))]
ListOfInt = Annotated[str, AfterValidator(split_string_validator(class_type=int))]
