import json

import pytest
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.signals import user_login_failed
from django.db import DatabaseError, connection, transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.common.exceptions import AuditError, AuditImmutable
from apps.common.models import AuditAction, AuditEvent, AuditOutcome
from apps.common.services import audit_context, record, suspend_audit

PASSWORD = "a-long-password-99"


def _change(event, field):
    return next(item for item in event.changes if item["field"] == field)


def _has_field(event, field):
    return any(item["field"] == field for item in event.changes)


@pytest.mark.integration
@pytest.mark.django_db
def test_record_stores_actor_request_and_redacts_secrets():
    user = User.objects.create_user("ada", "ada@example.com", PASSWORD)
    moment = timezone.now()

    with audit_context(
        actor=user,
        source="api",
        request_id="req-1",
        correlation_id="corr-1",
        ip_address="203.0.113.10",
        user_agent="audit-test",
        http_method="POST",
        path="/common/v1/audit/",
    ):
        event = record(
            action=AuditAction.CUSTOM,
            verb="demo.ping",
            message="hello",
            occurred_at=moment,
            extra={"password": "secret", "username": "ada"},
            changes={"city": ["Berlin", "Hamburg"], "token": ["old", "new"]},
            instance=user,
        )

    assert event is not None
    event.refresh_from_db()
    assert event.actor_id == user.pk
    assert event.actor_pk == str(user.pk)
    assert event.actor_kind == "user"
    assert event.actor_label
    assert event.action == AuditAction.CUSTOM
    assert event.verb == "demo.ping"
    assert event.outcome == AuditOutcome.SUCCESS
    assert event.source == "api"
    assert event.request_id == "req-1"
    assert event.correlation_id == "corr-1"
    assert event.ip_address == "203.0.113.10"
    assert event.user_agent == "audit-test"
    assert event.http_method == "POST"
    assert event.path == "/common/v1/audit/"
    assert event.object_pk == str(user.pk)
    assert event.content_type.app_label == "accounts"
    assert event.content_type.model == "user"
    assert event.occurred_at == moment
    assert event.extra == {"password": "[redacted]", "username": "ada"}
    assert _change(event, "city") == {"field": "city", "old": "Berlin", "new": "Hamburg"}
    assert _change(event, "token") == {"field": "token", "old": "[redacted]", "new": "[redacted]"}
    assert "secret" not in json.dumps(event.extra)


@pytest.mark.integration
@pytest.mark.django_db
def test_audit_events_cannot_be_changed_or_deleted():
    event = record(action=AuditAction.CUSTOM, verb="demo.locked", message="stay")

    event.message = "changed"
    with pytest.raises(AuditImmutable):
        event.save()
    with pytest.raises(AuditImmutable):
        event.delete()
    with pytest.raises(AuditImmutable):
        AuditEvent.objects.update(message="changed")
    with pytest.raises(AuditImmutable):
        AuditEvent.objects.all().delete()

    with pytest.raises(DatabaseError, match="immutable"):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE common_auditevent SET message = %s WHERE id = %s",
                    ["changed", event.id],
                )


@pytest.mark.integration
@pytest.mark.django_db
def test_suspend_audit_skips_explicit_and_model_events():
    user = User.objects.create_user("ada", "ada@example.com", PASSWORD)
    before = AuditEvent.objects.count()

    with suspend_audit():
        assert record(action=AuditAction.CUSTOM, verb="demo.silent") is None
        user.first_name = "Ada"
        user.save()

    assert AuditEvent.objects.count() == before
    user.refresh_from_db()
    assert user.first_name == "Ada"


@pytest.mark.integration
@pytest.mark.django_db
def test_user_changes_are_audited_without_storing_the_password():
    user = User.objects.create_user("ada", "ada@example.com", PASSWORD)
    created = AuditEvent.objects.get(verb="accounts.user.create", object_pk=str(user.pk))
    assert created.actor_kind == "system"
    assert _change(created, "password")["new"] == "[redacted]"
    assert PASSWORD not in json.dumps(created.changes)
    assert "pbkdf2" not in json.dumps(created.changes)

    unchanged = AuditEvent.objects.count()
    user.save()
    assert AuditEvent.objects.count() == unchanged

    with audit_context(actor=user, source="api", request_id="req-profile"):
        user.first_name = "Ada"
        user.save()
        user.set_password("another-long-password-99")
        user.save(update_fields=["password"])

    updates = AuditEvent.objects.filter(verb="accounts.user.update", object_pk=str(user.pk))
    rename = next(event for event in updates if _has_field(event, "first_name"))
    assert _change(rename, "first_name") == {"field": "first_name", "old": "", "new": "Ada"}
    assert rename.actor_id == user.pk
    assert rename.request_id == "req-profile"
    password_change = next(
        event
        for event in updates
        if any(
            item["field"] == "password" and item["old"] == "[redacted]" for item in event.changes
        )
    )
    assert _change(password_change, "password") == {
        "field": "password",
        "old": "[redacted]",
        "new": "[redacted]",
    }
    assert "another-long-password-99" not in json.dumps(password_change.changes)

    group = Group.objects.create(name="editors")
    user.groups.add(group)
    membership = next(
        event
        for event in AuditEvent.objects.filter(verb="accounts.user.update", object_pk=str(user.pk))
        if _has_field(event, "groups")
    )
    groups = _change(membership, "groups")
    assert groups["old"] == []
    assert groups["new"] == [str(group.pk)]


@pytest.mark.integration
@pytest.mark.django_db
def test_delete_keeps_the_actor_snapshot_after_the_account_is_gone():
    user = User.objects.create_user("ada", "ada@example.com", PASSWORD)
    user.first_name = "Ada"
    user.last_name = "Lovelace"
    user.save()
    pk = str(user.pk)

    with audit_context(actor=user, source="api"):
        user.delete()

    event = AuditEvent.objects.get(verb="accounts.user.delete", object_pk=pk)
    assert event.actor_id is None
    assert event.actor_pk == pk
    assert "Ada" in event.actor_label
    assert _change(event, "username")["old"] == "ada"
    assert _change(event, "username")["new"] is None
    assert User.objects.filter(pk=pk).exists() is False


@pytest.mark.integration
@pytest.mark.django_db
def test_failed_login_is_audited_without_the_password():
    user_login_failed.send(
        sender=User,
        credentials={"username": "ada", "password": PASSWORD},
        request=None,
    )

    event = AuditEvent.objects.get(verb="auth.login_failed")
    assert event.action == AuditAction.LOGIN_FAILED
    assert event.outcome == AuditOutcome.FAILURE
    assert event.actor_id is None
    assert event.extra == {"username": "ada"}
    assert PASSWORD not in json.dumps(event.extra)
    assert event.source == "signal"


@pytest.mark.integration
@pytest.mark.django_db
def test_record_rejects_unknown_actions_and_non_dict_extra():
    with pytest.raises(AuditError):
        record(action="nope", verb="demo.nope")
    with pytest.raises(AuditError):
        record(action=AuditAction.CUSTOM, verb="demo.extra", extra=["nope"])


@pytest.mark.integration
@pytest.mark.django_db
def test_audit_permission_exists_for_the_read_api():
    permission = Permission.objects.get(
        content_type__app_label="common",
        codename="view_auditevent",
    )
    assert permission.name
