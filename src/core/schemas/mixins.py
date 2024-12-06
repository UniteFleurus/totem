from typing import (
    Any,
    Callable,
)
from django.core.exceptions import FieldDoesNotExist, ObjectDoesNotExist
from ninja.schema import S
from pydantic import ValidationInfo, model_validator
from pydantic.functional_validators import ModelWrapValidatorHandler



class RelationalModelSchemaMixin:

    @model_validator(mode="wrap")
    @classmethod
    def _convert_relation_root_validator(
        cls, values: Any, handler: ModelWrapValidatorHandler[S], info: ValidationInfo
    ) -> Any:
        """ Note: problem of doing the conversion here is that it is not optimal
            for bulk operation, as relation will be fetched one by one. This is
            why is placed in a separated mixin.
        """
        result = handler(values)

        error = None
        model_class = cls.Meta.model
        for field_name, field in result.model_fields.items():
            field_extra = field.json_schema_extra or {}
            result_val = getattr(result, field_name, None)
            if result_val is not None:
                try:
                    model_field = model_class._meta.get_field(field_name)
                    if model_field.many_to_one:
                        try:
                            queryset = field_extra.get('queryset', model_field.related_model._default_manager)
                            queryset_only_fields = field_extra.get('queryset_only_fields', [])
                            slug_fname = field_extra.get('slug_field', 'pk')
                            if queryset_only_fields:
                                queryset = queryset.only(*queryset_only_fields)
                            obj = queryset.get(**{slug_fname: result_val})
                            setattr(result, field_name, obj)
                        except ObjectDoesNotExist:
                            error = f"Value in '{field_name}' does not match any {model_class._meta.verbose_name} identified by {str(result_val)}."

                except FieldDoesNotExist:
                    pass

        if error:
            raise ValueError(error)

        return result
