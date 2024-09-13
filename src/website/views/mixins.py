
from django.db.models.query import QuerySet
from django.http import Http404
from django.shortcuts import aget_object_or_404
from django.views.generic.base import TemplateResponseMixin, View

from website.models import Menu, Website, Widget
from website.website_widget import RendererWidgetRegistry

#-----------------------------------------
# Simple Rendering Helpers
#-----------------------------------------

class RenderContextMixin:
    """
    A default context mixin that passes the keyword arguments received by
    get_render_context_data() as the template context.
    """

    extra_context = None

    async def get_render_context_data(self):
        context = {}
        context.setdefault("view", self)
        if self.extra_context is not None:
            context.update(self.extra_context)
        return context

#-----------------------------------------
# Website Layout
#-----------------------------------------

class WebsiteRenderContextMixin(RenderContextMixin):

    async def get_render_context_data(self):
        context = await super().get_render_context_data()
        context.update(await self.get_website_context_data())
        return context

    async def get_website_context_data(self):
        # TODO : to be cached ?
        website = await Website.objects.afirst()
        if website.menu_id:
            hierarchy = await Menu.get_tree(website.menu_id)
            menu_tree = hierarchy.get_roots()[0]
        else:
            menu_tree = None

        widget_qs = Widget.objects.filter(position__startswith='FOOTER_')

        return {
            'website': website,
            'menu_tree': menu_tree,
            'widgets': RendererWidgetRegistry(widget_qs),
        }


class DetailRecordTemplateWebsiteView(TemplateResponseMixin, WebsiteRenderContextMixin, View):
    """ Helper class based view to render a single object """

    queryset = None

    # If you want to use object lookups other than pk, set 'lookup_field'.
    # For more complex lookup requirements override `get_object()`.
    lookup_field = 'pk'
    lookup_url_kwarg = None
    # Variable name the object will have in render context
    context_object_name = 'object'

    # Template
    template_name = None
    template_engine = 'jinja2'

    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )

        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset

    async def get_object(self):
        """
        Returns the object the view is displaying.

        You may want to override this if you need to provide non-standard
        queryset lookups.  Eg if objects are referenced using multiple
        keyword arguments in the url conf.
        """
        queryset = self.get_queryset()

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        try:
            return await aget_object_or_404(queryset, **filter_kwargs)
        except (TypeError, ValueError) as exc:
            raise Http404 from exc

        return None

    async def get_render_context_data(self):
        """Insert the single object into the context dict."""
        record = await self.get_object()  # might raise NotFound: Rather do it before fetching website context
        context = await super().get_render_context_data()
        if record:
            context["object"] = record
            if self.context_object_name:
                context[self.context_object_name] = record
        return context

    async def get(self, request, *args, **kwargs):
        context = await self.get_render_context_data()
        return self.render_to_response(context)
