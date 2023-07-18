from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from accounts.models import User

from .forms import UserChangeForm, UserCreationForm
from django.contrib.sessions.models import Session


# Register your models here.
class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = (
        "shopify_domain",
        "token",
        "access_scopes",
        "host",
        "is_admin",
        "created_at",
        "updated_at",
        "is_active",
    )
    list_filter = ("is_admin",)
    fieldsets = (
        (None, {"fields": ("password",)}),
        (
            "Information",
            {"fields": ("shopify_domain", "token", "host", "access_scopes")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_admin",
                    "is_superuser",
                    "user_permissions",
                    "groups",
                )
            },
        ),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (
            "Information",
            {
                "classes": ("wide",),
                "fields": (
                    "shopify_domain",
                    "token",
                ),
            },
        ),
        (
            "Credentials",
            {
                "fields": (
                    "password1",
                    "password2",
                )
            },
        ),
        (
            "Superuser",
            {
                "fields": (
                    "is_superuser",
                    "is_admin",
                    "user_permissions",
                    "groups",
                )
            },
        ),
    )
    search_fields = (
        "shopify_domain",
        "token",
    )
    ordering = ("shopify_domain",)
    filter_horizontal = ()


# Now register the new UserAdmin...
admin.site.register(User, UserAdmin)
admin.site.register(Session)
