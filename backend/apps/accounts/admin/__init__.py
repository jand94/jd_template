from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User


@admin.register(User)
class AccountUserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "salutation",
                    "title",
                    "first_name",
                    "middle_name",
                    "last_name",
                    "preferred_name",
                    "gender",
                    "pronouns",
                    "date_of_birth",
                    "place_of_birth",
                    "nationality",
                    "email",
                    "avatar",
                    "bio",
                ),
            },
        ),
        (_("Contact"), {"fields": ("phone", "mobile", "website")}),
        (
            _("Address"),
            {
                "fields": (
                    "street",
                    "house_number",
                    "address_line2",
                    "postal_code",
                    "city",
                    "region",
                    "country",
                ),
            },
        ),
        (_("Preferences"), {"fields": ("language", "timezone")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            _("Important dates"),
            {
                "fields": (
                    "last_login",
                    "date_joined",
                    "email_verified_at",
                    "phone_verified_at",
                    "terms_accepted_at",
                ),
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "usable_password",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "city",
        "is_staff",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "gender", "country", "groups")
    search_fields = (
        "username",
        "first_name",
        "middle_name",
        "last_name",
        "preferred_name",
        "email",
        "phone",
        "mobile",
        "city",
        "postal_code",
    )
    ordering = ("last_name", "first_name", "username")
