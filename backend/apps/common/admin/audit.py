import json

from django.contrib import admin
from django.utils.html import format_html, format_html_join
from django.utils.translation import gettext_lazy as _

from apps.common.models import AuditEvent


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    """Nur-Lese-Ansicht der Audit-Spur."""

    empty_value_display = "—"
    date_hierarchy = "occurred_at"
    list_per_page = 50
    show_facets = admin.ShowFacets.ALWAYS
    list_select_related = ("actor", "content_type")
    ordering = ("-occurred_at",)
    list_display = (
        "occurred_at",
        "action",
        "verb",
        "actor_label",
        "actor_kind",
        "object_repr",
        "outcome",
        "source",
        "request_id",
    )
    list_filter = (
        "action",
        "outcome",
        "source",
        "actor_kind",
        "content_type",
        ("occurred_at", admin.DateFieldListFilter),
    )
    search_fields = (
        "actor_label",
        "actor_pk",
        "verb",
        "object_repr",
        "object_pk",
        "request_id",
        "correlation_id",
        "message",
        "path",
        "ip_address",
    )
    readonly_fields = (
        "id",
        "occurred_at",
        "actor",
        "actor_pk",
        "actor_label",
        "actor_kind",
        "action",
        "verb",
        "content_type",
        "object_pk",
        "object_repr",
        "outcome",
        "message",
        "request_id",
        "correlation_id",
        "ip_address",
        "user_agent",
        "http_method",
        "path",
        "source",
        "changes_display",
        "extra_display",
    )
    fieldsets = (
        (
            _("Event"),
            {"fields": ("id", "occurred_at", "action", "verb", "outcome", "message", "source")},
        ),
        (
            _("Actor"),
            {"fields": ("actor", "actor_pk", "actor_label", "actor_kind")},
        ),
        (
            _("Target"),
            {"fields": ("content_type", "object_pk", "object_repr")},
        ),
        (
            _("Changes"),
            {"fields": ("changes_display", "extra_display")},
        ),
        (
            _("Request"),
            {
                "classes": ("collapse",),
                "fields": (
                    "request_id",
                    "correlation_id",
                    "ip_address",
                    "user_agent",
                    "http_method",
                    "path",
                ),
            },
        ),
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("actor", "content_type")

    @admin.display(description=_("changes"))
    def changes_display(self, obj):
        rows = []
        for change in obj.changes or []:
            if not isinstance(change, dict):
                continue
            rows.append(
                (
                    change.get("field", ""),
                    change.get("old"),
                    change.get("new"),
                )
            )
        if not rows:
            return self.empty_value_display
        return format_html_join("<br>", "{}: {} → {}", rows)

    @admin.display(description=_("extra"))
    def extra_display(self, obj):
        if not obj.extra:
            return self.empty_value_display
        text = json.dumps(obj.extra, indent=2, ensure_ascii=False, default=str)
        return format_html("<pre style='margin:0'>{}</pre>", text)
