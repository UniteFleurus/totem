from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from lxml import etree


def validate_html(value):
    if value is None:
        return None
    try:
        etree.fromstring(value)
    except etree.XMLSyntaxError as exc:
        raise ValidationError(_("Content is not a valid html.")) from exc
