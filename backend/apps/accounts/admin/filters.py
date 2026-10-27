from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class EmailVerifiedFilter(admin.SimpleListFilter):
    title = _("email verified")
    parameter_name = "email_verified"

    def lookups(self, request, model_admin):
        return (
            ("yes", _("Yes")),
            ("no", _("No")),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(email_verified_at__isnull=False)
        if self.value() == "no":
            return queryset.filter(email_verified_at__isnull=True)
        return queryset


class PhoneVerifiedFilter(admin.SimpleListFilter):
    title = _("phone verified")
    parameter_name = "phone_verified"

    def lookups(self, request, model_admin):
        return (
            ("yes", _("Yes")),
            ("no", _("No")),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(phone_verified_at__isnull=False)
        if self.value() == "no":
            return queryset.filter(phone_verified_at__isnull=True)
        return queryset
