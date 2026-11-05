import pytest
from django.apps import apps
from django.db import connection, models

from apps.accounts.models import User
from apps.common.models import AuditedModel, AuditEvent, StandardModel
from apps.common.services import audit_context

PASSWORD = "a-long-password-99"


def _unregister(model):
    label = model._meta.app_label
    name = model._meta.model_name
    apps.all_models[label].pop(name, None)
    apps.clear_cache()


@pytest.mark.integration
@pytest.mark.django_db
def test_standard_model_records_author_and_field_changes():
    author = User.objects.create_user("ada", "ada@example.com", PASSWORD)

    class Note(StandardModel, AuditedModel):
        title = models.CharField(max_length=40)
        secret = models.CharField(max_length=40, blank=True)

        class Meta:
            app_label = "common"

    try:
        with connection.schema_editor() as editor:
            editor.create_model(Note)
        with audit_context(actor=author, source="service", request_id="req-note"):
            note = Note.objects.create(title="alpha", secret="s3cret")
            assert note.created_by_id == author.pk
            assert note.updated_by_id == author.pk
            note.title = "beta"
            note.secret = "next"
            note.save(update_fields=["title", "secret"])
            note_pk = str(note.pk)
            note.delete()
        created = AuditEvent.objects.get(verb="common.note.create", request_id="req-note")
        created_secret = next(item for item in created.changes if item["field"] == "secret")
        assert created_secret == {"field": "secret", "old": None, "new": "[redacted]"}
        assert "s3cret" not in str(created.changes)
        updated = AuditEvent.objects.get(verb="common.note.update", request_id="req-note")
        title = next(item for item in updated.changes if item["field"] == "title")
        secret = next(item for item in updated.changes if item["field"] == "secret")
        assert title == {"field": "title", "old": "alpha", "new": "beta"}
        assert secret == {"field": "secret", "old": "[redacted]", "new": "[redacted]"}
        assert "updated_at" not in {item["field"] for item in updated.changes}
        deleted = AuditEvent.objects.get(verb="common.note.delete", request_id="req-note")
        assert deleted.object_pk == note_pk
        assert next(item for item in deleted.changes if item["field"] == "title")["old"] == "beta"
    finally:
        _unregister(Note)
