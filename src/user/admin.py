from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUseAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from user.models import User, UserRole, UserRoleRelation

# Removing Django groups from the admin panel as they are no longer used
admin.site.unregister(Group)


# -------------------------------------
# User
# -------------------------------------

class RoleRelationInline(admin.TabularInline):
    model = UserRoleRelation
    extra = 0


class UserAdmin(BaseUseAdmin):
    list_display = BaseUseAdmin.list_display + ("user_type",)
    list_filter = ("user_type", "is_active")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Permissions"),
            {
                "fields": ("is_active", "is_staff", "is_superuser", "user_type",),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2"),
            },
        ),
    )
    inlines = (RoleRelationInline,)


admin.site.register(User, UserAdmin)


# -------------------------------------
# User Role
# -------------------------------------

class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


admin.site.register(UserRole, UserRoleAdmin)
