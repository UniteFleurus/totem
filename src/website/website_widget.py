from django.core import exceptions
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe


_REGISTRY = {}  # widget_type -> instance of Widget Type


def get_widget_type_choices():
    return {widget_type.widget_type: widget_type.widget_type_name for widget_type in _REGISTRY.values() if widget_type.widget_type is not None}

def get_widget_type(widget_type, raise_if_not_found=False):
    widget_type_instance = _REGISTRY.get(widget_type)
    if widget_type_instance is None and raise_if_not_found:
        raise ValueError(f"`{widget_type}` not found in registry.")
    return widget_type_instance

#--------------------------------------------
# Widget Lazy Render Registry
#--------------------------------------------

class RendererWidgetRegistry:

    def __init__(self, widget_qs):
        self._widget_qs = widget_qs
        self._position_map = None

    def __getitem__(self, position):
        if self._position_map is None:
            self._position_map = {w.position: w for w in self._widget_qs}

        try:
            return self._position_map[position].rendered_content
        except KeyError:
            return ''

#--------------------------------------------
# Widget Type Class
#--------------------------------------------

class WebsiteWidgetMetaclass(type):
    def __new__(cls, name, bases, attrs):
        new_cls = type.__new__(cls, name, bases, attrs)
        for attr in ['widget_type', 'widget_type_name']:
            if not hasattr(new_cls, attr):
                raise ValueError(f"`{attr}` must be set when implementing a widget type class !")
        if new_cls.widget_type and new_cls.widget_type in _REGISTRY:
            raise ValueError(f"{new_cls.widget_type} is a widget type already defined.")

        _REGISTRY[new_cls.widget_type] = new_cls()
        return new_cls


class AbstractWebsiteWidget(metaclass=WebsiteWidgetMetaclass):
    widget_type = None
    widget_type_name = None
    template_name = None
    template_engine = 'jinja2'

    validation_required_fields = []

    def render(self, widget_instance):
        return mark_safe(render_to_string(self.template_name, self.get_render_context(widget_instance), using=self.template_engine))

    def get_render_context(self, widget_instance):
        raise NotImplementedError(
            "Widget Type class must implement the get_render_context method !"
        )

    def is_valid(self, widget_instance, raise_exception=False):
        errors = {}
        for fname in self.validation_required_fields:
            if getattr(widget_instance, fname, None) is None:
                errors[fname] = f"This field is required as the widgte type is `{self.widget_type_name}`."

        # ensure other parameters field are set to None
        for fname in self.validation_null_fields:
            if getattr(widget_instance, fname, None) is not None:
                errors[fname] = f"This field must be unset as the widgte type is `{self.widget_type_name}`."

        if errors:
            if raise_exception:
                raise exceptions.ValidationError(errors)
            return False
        return True

    @property
    def validation_null_fields(self):
        from website.models import Widget
        parameters_field_names = [f.name for f in Widget._meta.get_fields() if f.name.startswith('param_')]
        return list(set(parameters_field_names) - set(self.validation_required_fields))


class CustomHTMLWidget(AbstractWebsiteWidget):
    widget_type = 'custom_html'
    widget_type_name = "Custom HTML Block"
    template_name = "website/widgets/custom_html.html"

    validation_required_fields = ['param_content']

    def get_render_context(self, widget_instance):
        return {
            "title": widget_instance.title,
            "content": widget_instance.param_content,
        }


class LastUpdatePageWidget(AbstractWebsiteWidget):
    widget_type = 'last_update_page'
    widget_type_name = "Last Updated Page"
    template_name = "website/widgets/last_update_page.html"

    validation_required_fields = ['param_limit_item']

    def get_render_context(self, widget_instance):
        from website.models import Page
        return {
            "title": widget_instance.title,
            "pages": Page.objects.filter(is_published=True).order_by('-update_date')[0:widget_instance.param_limit_item],
        }
