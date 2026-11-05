import pytest
from django.apps import apps
from django.db import connection, models

from apps.accounts.models import User
from apps.common.models import AuditedModel, AuditEvent, SoftDeleteModel, StandardModel
from apps.common.services import audit_context

PASSWORD = "a-long-password-99"


def _unregister(model):
    apps.all_models[model._meta.app_label].pop(model._meta.model_name, None)
    apps.clear_cache()


def _change(event, field):
    return next(item for item in event.changes if item["field"] == field)


@pytest.mark.integration
@pytest.mark.django_db
def test_soft_delete_hides_the_row_and_records_delete_and_restore():
    author = User.objects.create_user("ada", "ada@example.com", PASSWORD)

    class Draft(StandardModel, SoftDeleteModel, AuditedModel):
        title = models.CharField(max_length=40)

        class Meta:
            app_label = "common"

    try:
        assert Draft._meta.base_manager_name == "all_objects"
        with connection.schema_editor() as editor:
            editor.create_model(Draft)
        with audit_context(actor=author, source="service", request_id="req-draft"):
            draft = Draft.objects.create(title="alpha")
            draft_pk = draft.pk
            deleted, _details = draft.delete()
            assert deleted == 1
            assert draft.is_deleted is True
            assert draft.deleted_by_id == author.pk
            assert Draft.objects.filter(pk=draft_pk).exists() is False
            stored = Draft.all_objects.get(pk=draft_pk)
            assert stored.deleted_at is not None
            again, _details = draft.delete()
            assert again == 0
            stored.restore()
            stored.restore()
            assert stored.deleted_at is None
            assert stored.deleted_by_id is None
            assert Draft.objects.filter(pk=draft_pk).exists() is True

            other = Draft.objects.create(title="beta")
            other_pk = other.pk
            marked, _details = Draft.objects.filter(pk=other_pk).delete()
            assert marked == 1
            assert Draft.objects.filter(pk=other_pk).exists() is False
            gone = Draft.all_objects.get(pk=other_pk)
            gone.hard_delete()
            assert Draft.all_objects.filter(pk=other_pk).exists() is False
            third = Draft.objects.create(title="gamma")
            third_pk = third.pk
            purged_count, _details = Draft.all_objects.filter(pk=third_pk).hard_delete()
            assert purged_count == 1
            assert Draft.all_objects.filter(pk=third_pk).exists() is False

        removed = AuditEvent.objects.get(
            verb="common.draft.delete",
            object_pk=str(draft_pk),
            request_id="req-draft",
        )
        assert removed.action == "delete"
        assert removed.extra == {"soft": True}
        assert removed.actor_id == author.pk
        assert _change(removed, "deleted_at")["old"] is None
        assert _change(removed, "deleted_at")["new"] is not None
        assert _change(removed, "deleted_by")["new"] == author.pk
        assert "title" not in {item["field"] for item in removed.changes}
        assert (
            AuditEvent.objects.filter(
                verb="common.draft.delete",
                object_pk=str(draft_pk),
            ).count()
            == 1
        )

        assert (
            AuditEvent.objects.filter(verb="common.draft.restore", object_pk=str(draft_pk)).count()
            == 1
        )
        restored = AuditEvent.objects.get(verb="common.draft.restore", object_pk=str(draft_pk))
        assert restored.action == "restore"
        assert restored.extra == {"soft": True}
        assert _change(restored, "deleted_at")["new"] is None
        assert _change(restored, "deleted_by")["new"] is None

        purged = AuditEvent.objects.get(
            verb="common.draft.delete",
            object_pk=str(other_pk),
            extra={},
        )
        assert purged.extra == {}
        assert _change(purged, "title") == {"field": "title", "old": "beta", "new": None}
    finally:
        _unregister(Draft)
