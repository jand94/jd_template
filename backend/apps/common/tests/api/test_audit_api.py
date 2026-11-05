import pytest
from django.contrib.auth.models import Permission
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import User
from apps.common.models import AuditAction, AuditEvent
from apps.common.services import audit_context, record

PASSWORD = "a-long-password-99"


def _grant(user):
    permission = Permission.objects.get(
        content_type__app_label="common",
        codename="view_auditevent",
    )
    user.user_permissions.add(permission)
    return user


@pytest.mark.api
@pytest.mark.django_db
def test_audit_list_requires_authentication_and_permission(api_client):
    denied = api_client.get(reverse("common:audit-list"))
    assert denied.status_code == 401

    user = User.objects.create_user("ada", "ada@example.com", PASSWORD)
    api_client.force_login(user)
    forbidden = api_client.get(reverse("common:audit-list"))
    assert forbidden.status_code == 403

    user.is_active = False
    user.save()
    _grant(user)
    api_client.force_login(user)
    # DRF-SessionAuthentication behandelt inaktive Konten als anonym.
    inactive = api_client.get(reverse("common:audit-list"))
    assert inactive.status_code == 401


@pytest.mark.api
@pytest.mark.django_db
def test_audit_list_filters_and_detail_are_read_only(api_client):
    auditor = _grant(User.objects.create_user("auditor", "auditor@example.com", PASSWORD))
    subject = User.objects.create_user("ada", "ada@example.com", PASSWORD)
    moment = timezone.now()
    with audit_context(actor=auditor, source="api", request_id="req-listed"):
        event = record(
            action=AuditAction.CUSTOM,
            verb="demo.listed",
            instance=subject,
            message="listed",
            occurred_at=moment,
        )
        record(action=AuditAction.CUSTOM, verb="demo.other", message="other")

    api_client.force_login(auditor)
    listed = api_client.get(
        reverse("common:audit-list"),
        {"verb": "demo.listed", "actor": auditor.pk, "request_id": "req-listed"},
    )

    assert listed.status_code == 200
    body = listed.json()
    assert body["count"] == 1
    assert body["results"][0]["id"] == str(event.id)
    assert body["results"][0]["verb"] == "demo.listed"
    assert body["results"][0]["content_type"] == "accounts.user"
    assert body["results"][0]["actor"] == auditor.pk
    assert body["results"][0]["object_pk"] == str(subject.pk)
    assert body["results"][0]["request_id"] == "req-listed"

    detail = api_client.get(reverse("common:audit-detail", kwargs={"event_id": event.id}))
    assert detail.status_code == 200
    assert detail.json()["message"] == "listed"

    missing = api_client.get(
        reverse(
            "common:audit-detail",
            kwargs={"event_id": "11111111-1111-1111-1111-111111111111"},
        )
    )
    assert missing.status_code == 404

    rejected = api_client.get(reverse("common:audit-list"), {"action": "nope"})
    assert rejected.status_code == 400

    created = api_client.post(reverse("common:audit-list"), {}, format="json")
    assert created.status_code == 405
    assert AuditEvent.objects.filter(verb="demo.listed").count() == 1


@pytest.mark.api
@pytest.mark.django_db
def test_profile_update_captures_request_context(api_client):
    user = _grant(User.objects.create_user("ada", "ada@example.com", PASSWORD))
    api_client.force_login(user)

    response = api_client.patch(
        reverse("accounts:me"),
        {"first_name": "Ada"},
        format="json",
        HTTP_X_REQUEST_ID="req-from-header",
        HTTP_X_CORRELATION_ID="corr-from-header",
        HTTP_X_REAL_IP="198.51.100.20",
        HTTP_USER_AGENT="profile-test",
    )

    assert response.status_code == 200
    event = AuditEvent.objects.get(
        verb="accounts.user.update",
        object_pk=str(user.pk),
        request_id="req-from-header",
    )
    assert event.request_id == "req-from-header"
    assert event.correlation_id == "corr-from-header"
    assert event.ip_address == "198.51.100.20"
    assert event.user_agent == "profile-test"
    assert event.http_method == "PATCH"
    assert event.path.endswith("/accounts/v1/me/")
    assert event.source == "api"
    assert event.actor_id == user.pk
    assert {"field": "first_name", "old": "", "new": "Ada"} in event.changes


@pytest.mark.api
@pytest.mark.django_db
def test_audit_filters_cover_target_time_search_and_invalid_values(api_client):
    auditor = _grant(User.objects.create_user("auditor", "auditor@example.com", PASSWORD))
    subject = User.objects.create_user("ada", "ada@example.com", PASSWORD)
    with audit_context(actor=auditor, source="api"):
        event = record(
            action=AuditAction.ACCESS,
            verb="demo.search",
            instance=subject,
            message="needle",
            occurred_at=timezone.now(),
        )
    api_client.force_login(auditor)
    found = api_client.get(
        reverse("common:audit-list"),
        {
            "q": "needle",
            "content_type": "accounts.user",
            "object_pk": subject.pk,
            "actor_kind": "user",
            "outcome": "success",
            "source": "api",
            "occurred_after": "2020-01-01",
            "occurred_before": "2100-01-01T00:00:00Z",
            "correlation_id": "",
        },
    )
    assert found.status_code == 200
    assert found.json()["count"] == 1
    assert found.json()["results"][0]["id"] == str(event.id)
    assert found.json()["results"][0]["content_type"] == "accounts.user"

    bare = record(action=AuditAction.CUSTOM, verb="demo.bare", message="no-target")
    detail = api_client.get(reverse("common:audit-detail", kwargs={"event_id": bare.id}))
    assert detail.status_code == 200
    assert detail.json()["content_type"] is None

    assert api_client.get(reverse("common:audit-list"), {"actor": "nope"}).status_code == 400
    assert (
        api_client.get(reverse("common:audit-list"), {"content_type": "accounts"}).status_code
        == 400
    )
    assert (
        api_client.get(
            reverse("common:audit-list"),
            {"content_type": "accounts.missing"},
        ).status_code
        == 400
    )
    assert (
        api_client.get(reverse("common:audit-list"), {"occurred_after": "yesterday"}).status_code
        == 400
    )
    assert api_client.get(reverse("common:audit-list"), {"source": "nope"}).status_code == 400


@pytest.mark.api
@pytest.mark.django_db
def test_login_and_logout_are_audited(api_client):
    User.objects.create_user("ada", "ada@example.com", PASSWORD)

    logged_in = api_client.post(
        reverse("accounts:login"),
        {"username": "ada", "password": PASSWORD},
        format="json",
    )
    assert logged_in.status_code == 200
    login_event = AuditEvent.objects.get(verb="auth.login")
    assert login_event.action == "login"
    assert login_event.outcome == "success"
    assert login_event.actor_id is not None
    assert PASSWORD not in str(login_event.extra)

    logged_out = api_client.post(reverse("accounts:logout"), {}, format="json")
    assert logged_out.status_code == 204
    assert AuditEvent.objects.filter(verb="auth.logout").exists()
