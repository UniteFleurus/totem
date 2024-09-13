from django.db import models
from django.utils import timezone


class WebsitePublishedMixin(models.Model):
    slug = models.SlugField(
        "Slug",
        max_length=256,
        null=False,
        blank=False,
        help_text="URL part identifying the page."
    )
    is_published = models.BooleanField(
        "Is Published", null=False, blank=False, default=False, help_text="Is published on the website.")
    date_published = models.DateTimeField(
        "Publication Date", null=True, blank=True, help_text="Date of the last publication of the document.")

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=['slug'], name='%(class)s_unique_slug'
            ),
        ]

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if update_fields and 'is_published' in update_fields:
            self.date_published = timezone.now()
            update_fields.append('date_published')
        return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
