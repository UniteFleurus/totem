from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUseAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from django import forms

from user.models import User, UserRole, UserRoleRelation
from user.access_policy import access_policy
from user.access_rights import get_permission_choices


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
        (_("Personal info"), {"fields": ("first_name", "last_name", "email", "avatar")}),
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


class UserRoleAdminForm(forms.ModelForm):
    permissions = forms.MultipleChoiceField(
        choices=lambda: get_permission_choices(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    rules = forms.MultipleChoiceField(
        choices=lambda: access_policy.get_rule_choices(model_name_prefix=True),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = UserRole
        fields = "__all__"



class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("id", "name")

    form = UserRoleAdminForm


admin.site.register(UserRole, UserRoleAdmin)
