from django.db import models

from core import fields
from website.models.mixins import WebsitePublishedMixin


class Page(WebsitePublishedMixin):
    title = models.CharField(
        "Title", max_length=256, null=False, blank=False)
    content = fields.HtmlField(
        "Content", null=False, blank=False, help_text="HTML content")
    update_date = models.DateTimeField("Update Date", auto_now=True)

    @property
    def url(self):
        return f"/page/{self.slug}/"

    class Meta:
        verbose_name = "Page"
        verbose_name_plural = "Pages"
        constraints = WebsitePublishedMixin.Meta.constraints

    def __str__(self):
        return self.title
