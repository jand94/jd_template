from django import forms
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.accounts.admin.filters import EmailVerifiedFilter, PhoneVerifiedFilter
from apps.accounts.admin.forms import AccountUserChangeForm, AccountUserCreationForm
from apps.accounts.models import User


@admin.register(User)
class AccountUserAdmin(UserAdmin):
    """Verwaltung des Benutzerkontos inklusive Profil, Adresse und Rechten."""

    form = AccountUserChangeForm
    add_form = AccountUserCreationForm
    empty_value_display = "—"
    save_on_top = True
    list_per_page = 50
    show_facets = admin.ShowFacets.ALWAYS
    date_hierarchy = "date_joined"
    search_help_text = _("Name, email, phone, city, or postal code.")
    ordering = ("last_name", "first_name", "username")
    list_display_links = ("username", "email")
    filter_horizontal = ("groups", "user_permissions")
    radio_fields = {
        "salutation": admin.HORIZONTAL,
        "gender": admin.HORIZONTAL,
    }
    readonly_fields = (
        "age",
        "formatted_address",
        "is_email_verified",
        "is_phone_verified",
        "last_login",
        "date_joined",
    )
    list_display = (
        "username",
        "email",
        "display_name",
        "city",
        "country",
        "is_active",
        "is_staff",
        "is_email_verified",
        "date_joined",
    )
    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
        "gender",
        "salutation",
        "country",
        "groups",
        EmailVerifiedFilter,
        PhoneVerifiedFilter,
        ("date_joined", admin.DateFieldListFilter),
        ("date_of_birth", admin.EmptyFieldListFilter),
        ("city", admin.EmptyFieldListFilter),
    )
    search_fields = (
        "username",
        "email",
        "first_name",
        "middle_name",
        "last_name",
        "preferred_name",
        "phone",
        "mobile",
        "street",
        "city",
        "postal_code",
        "country",
    )
    actions = (
        "activate_users",
        "deactivate_users",
        "mark_email_verified",
        "mark_phone_verified",
    )
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "salutation",
                    "title",
                    ("first_name", "middle_name", "last_name"),
                    "preferred_name",
                    ("gender", "pronouns"),
                    ("date_of_birth", "age"),
                    ("place_of_birth", "nationality"),
                    "avatar",
                    "bio",
                ),
            },
        ),
        (
            _("Contact"),
            {
                "fields": (
                    "email",
                    "is_email_verified",
                    ("phone", "mobile"),
                    "is_phone_verified",
                    "website",
                ),
            },
        ),
        (
            _("Address"),
            {
                "fields": (
                    "formatted_address",
                    ("street", "house_number"),
                    "address_line2",
                    ("postal_code", "city"),
                    ("region", "country"),
                ),
            },
        ),
        (
            _("Preferences"),
            {
                "classes": ("collapse",),
                "fields": ("language", "timezone"),
            },
        ),
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
                "classes": ("collapse",),
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
                "description": _(
                    "After saving, the profile, address, and permissions can be edited."
                ),
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

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "bio":
            kwargs["widget"] = forms.Textarea(attrs={"rows": 4, "cols": 80})
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    @admin.display(description=_("name"), ordering="last_name")
    def display_name(self, obj):
        return obj.get_display_name()

    @admin.display(description=_("age"), ordering="date_of_birth")
    def age(self, obj):
        if obj.age is None:
            return self.empty_value_display
        return obj.age

    @admin.display(description=_("postal address"))
    def formatted_address(self, obj):
        return obj.formatted_address() or self.empty_value_display

    @admin.display(description=_("email verified"), boolean=True, ordering="email_verified_at")
    def is_email_verified(self, obj):
        return obj.is_email_verified

    @admin.display(description=_("phone verified"), boolean=True, ordering="phone_verified_at")
    def is_phone_verified(self, obj):
        return obj.is_phone_verified

    @admin.action(description=_("Activate selected users"))
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            _("Activated %(count)s users.") % {"count": updated},
            messages.SUCCESS,
        )

    @admin.action(description=_("Deactivate selected users"))
    def deactivate_users(self, request, queryset):
        actor_id = getattr(request.user, "pk", None)
        updated = queryset.exclude(pk=actor_id).update(is_active=False)
        skipped_self = actor_id is not None and queryset.filter(pk=actor_id).exists()
        if skipped_self:
            self.message_user(
                request,
                _(
                    "Deactivated %(count)s users. Your own account was left active."
                )
                % {"count": updated},
                messages.WARNING,
            )
            return
        self.message_user(
            request,
            _("Deactivated %(count)s users.") % {"count": updated},
            messages.SUCCESS,
        )

    @admin.action(description=_("Mark email as verified"))
    def mark_email_verified(self, request, queryset):
        updated = queryset.filter(email_verified_at__isnull=True).update(
            email_verified_at=timezone.now()
        )
        self.message_user(
            request,
            _("Marked email as verified for %(count)s users.") % {"count": updated},
            messages.SUCCESS,
        )

    @admin.action(description=_("Mark phone as verified"))
    def mark_phone_verified(self, request, queryset):
        updated = queryset.filter(phone_verified_at__isnull=True).update(
            phone_verified_at=timezone.now()
        )
        self.message_user(
            request,
            _("Marked phone as verified for %(count)s users.") % {"count": updated},
            messages.SUCCESS,
        )
