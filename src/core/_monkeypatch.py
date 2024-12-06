
def monkeypatch_ninja():
    from typing import Any, Callable, Dict, List, Tuple, Type, TypeVar, Union, no_type_check

    from ninja.orm import fields as ninja_fields
    from ninja.orm import factory as ninja_factory

    _origin_get_schema_field = ninja_fields.get_schema_field

    @no_type_check
    def get_schema_field(
        field: Any, *, depth: int = 0, optional: bool = False
    ) -> Tuple:
        python_type, fieldinfo = _origin_get_schema_field(field, depth=depth, optional=optional)

        if not field.is_relation:
            if not field.null:
                internal_type = field.get_internal_type()
                python_type = ninja_fields.TYPES[internal_type]

        return python_type, fieldinfo

    ninja_fields.get_schema_field = get_schema_field
    ninja_factory.get_schema_field = get_schema_field
