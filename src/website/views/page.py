
from website.models import Page
from website.models import Widget
from website.views.mixins import TemplateResponseMixin, WebsiteRenderContextMixin, View, DetailRecordTemplateWebsiteView
from website.website_widget import RendererWidgetRegistry


class PageView(DetailRecordTemplateWebsiteView):

    queryset = Page.objects.filter(is_published=True)
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'
    template_name = 'website/page.html'
    context_object_name = 'page'


class HomePageView(TemplateResponseMixin, WebsiteRenderContextMixin, View):

    template_name = 'website/homepage.html'
    template_engine = 'jinja2'

    async def get_website_context_data(self):
        context = await super().get_website_context_data()

        widget_qs = Widget.objects.filter(position__startswith='HOMEPAGE_')
        context['homepage_widgets'] = RendererWidgetRegistry(widget_qs)

        return context

    async def get(self, request, *args, **kwargs):
        context = await self.get_render_context_data()
        return self.render_to_response(context)
