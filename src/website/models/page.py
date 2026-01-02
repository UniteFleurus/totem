from django.db import models

from core import fields
from website.models.mixins import WebsitePublishedMixin


class Page(WebsitePublishedMixin):
    title = models.CharField(
        "Title", max_length=256, null=False, blank=False)
    content = fields.HtmlField(
        "Content", null=False, blank=False, help_text="HTML content")
    update_date = models.DateTimeField("Update Date", auto_now=True)
    user = models.ForeignKey('user.User', verbose_name="Author", null=True, blank=True, on_delete=models.SET_NULL, help_text="Author of the web page.")

    @property
    def url(self):
        return f"/page/{self.slug}/"

    class Meta(WebsitePublishedMixin.Meta):
        verbose_name = "Page"
        verbose_name_plural = "Pages"
        constraints = WebsitePublishedMixin.Meta.constraints

    def __str__(self):  # pylint: disable=E0307
        return self.title
