from django.contrib import admin

from website.models import Page, Menu, Website, Widget

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
