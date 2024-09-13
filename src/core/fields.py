from lxml import etree
from django import forms
from django.core import exceptions
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.utils.html import safe_attrs, allowed_tags, tags_to_kill, tags_to_remove, Cleaner
from core.validators import validate_html


class HtmlFieldMixin:
    default_error_messages = {
        "invalid": _(
            "The content must be a valid and parsable HTML code."
        ),
    }

    def __init__(self, *args, sanitize=True, sanitize_tags=True, sanitize_attributes=True, sanitize_style=False, sanitize_form=True, strip_style=False, strip_classes=False, **kwargs):
        super().__init__(*args, **kwargs)

        # sanitize: whether value must be sanitized
        # sanitize_tags: whether to sanitize tags (only a white list of tag is accepted)
        # sanitize_attributes: whether to sanitize attributes (only a white list of attributes is accepted)
        # sanitize_style: whether to sanitize style attributes
        # sanitize_form: whether to sanitize forms
        # strip_style: whether to strip style attributes (removed and therefore not sanitized)
        # strip_classes: whether to strip classes attributes
        self.sanitize = sanitize
        self.sanitize_tags = sanitize_tags
        self.sanitize_attributes = sanitize_attributes
        self.sanitize_style = sanitize_style
        self.sanitize_form = sanitize_form
        self.strip_style = strip_style
        self.strip_classes = strip_classes

        if sanitize:
            self._cleaner = self._get_html_cleaner(sanitize_tags=sanitize_tags, sanitize_attributes=sanitize_attributes,
                                                   sanitize_style=sanitize_style, sanitize_form=sanitize_form, strip_style=strip_style, strip_classes=strip_classes)
        else:
            self._cleaner = None

    def _get_html_cleaner(self, sanitize_tags=True, sanitize_attributes=False, sanitize_style=False, sanitize_form=True, strip_style=False, strip_classes=False):
        kwargs = {
            'page_structure': True,
            'style': strip_style,              # True = remove style tags/attrs
            'sanitize_style': sanitize_style,  # True = sanitize styling
            'forms': sanitize_form,            # True = remove form tags
            'remove_unknown_tags': False,
            'comments': False,
            'processing_instructions': False
        }
        if sanitize_tags:
            kwargs['allow_tags'] = allowed_tags
            kwargs.update({
                'kill_tags': tags_to_kill,
                'remove_tags': tags_to_remove,
            })

        # keep all attributes in order to keep "style"
        if sanitize_attributes:
            if strip_classes:
                current_safe_attrs = safe_attrs - frozenset(['class'])
            else:
                current_safe_attrs = safe_attrs
            kwargs.update({
                'safe_attrs_only': True,
                'safe_attrs': current_safe_attrs,
            })
        return Cleaner(**kwargs)

    def to_python(self, value):
        value = super().to_python(value)
        if value is None:
            return None
        # is valid input
        validate_html(value)  # raise a validation error
        # try to sanitize
        if self._cleaner:
            try:
                # some corner cases make the parser crash (such as <SCRIPT/XSS SRC=\"http://ha.ckers.org/xss.js\"></SCRIPT> in test_mail)
                value = self._cleaner.clean_html(value)
                assert isinstance(value, str)
            except etree.ParserError:
                raise exceptions.ValidationError(
                    self.error_messages["invalid"],
                    code="invalid",
                )
        return value


class HtmlCharField(HtmlFieldMixin, forms.CharField):
   pass


class HtmlField(HtmlFieldMixin, models.TextField):
    description = _("Html")

    def to_python(self, value):
        if value == '' and self.null:
            return None
        return super().to_python(value)

    def formfield(self, form_class=HtmlCharField, **kwargs):
        kwargs['sanitize'] = self.sanitize
        kwargs['sanitize_tags'] = self.sanitize_tags
        kwargs['sanitize_attributes'] = self.sanitize_attributes
        kwargs['sanitize_style'] = self.sanitize_style
        kwargs['sanitize_form'] = self.sanitize_form
        kwargs['strip_style'] = self.strip_style
        kwargs['strip_classes'] = self.strip_classes
        kwargs['empty_value'] = None if self.null else "" # force NULL instead of empty string
        return super().formfield(form_class=form_class, **kwargs)
