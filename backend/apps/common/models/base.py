import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.services.context import current_actor


class UUIDModel(models.Model):
    """Primärschlüssel als UUID, unabhängig von der Datenbanksequenz."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimeStampedModel(models.Model):
    """Zeitpunkt der Anlage und der letzten Änderung."""

    created_at = models.DateTimeField(_("created at"), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        abstract = True


class AuthoredModel(models.Model):
    """Konto, das den Datensatz angelegt und zuletzt geändert hat.

    Beide Verweise bleiben leer, wenn kein angemeldetes Konto im Audit-Kontext
    steht, zum Beispiel in einer Management-Command oder einem Task.
    """

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("created by"),
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("updated by"),
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        actor = current_actor()
        if actor is not None and getattr(actor, "pk", None):
            if self._state.adding and self.created_by_id is None:
                self.created_by = actor
            self.updated_by = actor
            update_fields = kwargs.get("update_fields")
            if update_fields is not None:
                fields = set(update_fields)
                if self._state.adding:
                    fields.add("created_by")
                fields.add("updated_by")
                kwargs["update_fields"] = list(fields)
        super().save(*args, **kwargs)


class StandardModel(UUIDModel, TimeStampedModel, AuthoredModel):
    """Übliche Basis für Fachmodelle: UUID, Zeitstempel und Autorenschaft."""

    class Meta:
        abstract = True
