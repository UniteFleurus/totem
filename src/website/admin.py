from django.contrib import admin
from django import forms

from website.models import Page, Media, Menu, Website, Widget


# -------------------------------------
# Media
# -------------------------------------

class MediaAdminForm(forms.ModelForm):

    def clean(self):
        if self.instance._state.adding: # creation flow
            memory_file = self.cleaned_data.get('content') # InMemoryUploadedFile

            if memory_file:
                values = Media.precompute_values(memory_file.file.getvalue(), memory_file.name)
                self.cleaned_data.update(values)

        return super().clean()

    def save(self, commit=True):
        for field in self.cleaned_data:
            setattr(self.instance, field, self.cleaned_data.get(field))
        return super().save(commit=commit)


class MediaAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "mimetype")
    readonly_fields = ["checksum", "mimetype"]

    form = MediaAdminForm

    def get_fields(self, request, obj=None):
        if obj is None:
            return ["content"]
        return super().get_fields(request, obj=obj)

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj=obj)
        if obj is None:
            fields += ['content']
        return fields

admin.site.register(Media, MediaAdmin)


# -------------------------------------
# Website Page
# -------------------------------------

class PageAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_published")


admin.site.register(Page, PageAdmin)


# -------------------------------------
# Website Menu
# -------------------------------------

class MenuAdmin(admin.ModelAdmin):
    list_display = ("name", "sequence", "page", "link")


admin.site.register(Menu, MenuAdmin)


# -------------------------------------
# Website
# -------------------------------------

class WebsiteAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "headline")


admin.site.register(Website, WebsiteAdmin)

# -------------------------------------
# Widget
# -------------------------------------

class WidgetAdmin(admin.ModelAdmin):
    list_display = ("title", "widget_type", "position")


admin.site.register(Widget, WidgetAdmin)
