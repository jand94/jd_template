import pytest
from django.contrib import admin
from django.test import RequestFactory

from apps.accounts.models import User
from apps.common.admin import AuditEventAdmin
from apps.common.models import AuditAction, AuditEvent
from apps.common.services import record

PASSWORD = "a-long-password-99"


@pytest.mark.integration
@pytest.mark.django_db
def test_audit_admin_is_read_only_and_renders_changes():
    event = record(
        action=AuditAction.CUSTOM,
        verb="demo.admin",
        message="shown",
        changes=[{"field": "city", "old": "Berlin", "new": "Hamburg"}],
        extra={"note": "kept"},
    )
    model_admin = AuditEventAdmin(AuditEvent, admin.site)
    request = RequestFactory().get("/admin/common/auditevent/")
    request.user = User.objects.create_superuser("root", "root@example.com", PASSWORD)
    noisy = type("Row", (), {})()
    noisy.changes = [{"field": "city", "old": "Berlin", "new": "Hamburg"}, "ignore-me"]
    noisy.extra = {"note": "kept"}
    empty = type("Row", (), {"changes": [], "extra": {}})()

    assert model_admin.has_add_permission(request) is False
    assert model_admin.has_change_permission(request, event) is False
    assert model_admin.has_delete_permission(request, event) is False
    assert "city" in str(model_admin.changes_display(noisy))
    assert "kept" in str(model_admin.extra_display(noisy))
    assert model_admin.changes_display(empty) == model_admin.empty_value_display
    assert model_admin.extra_display(empty) == model_admin.empty_value_display
    assert "demo.admin" in str(event)
    assert model_admin.get_queryset(request).filter(pk=event.pk).exists()
