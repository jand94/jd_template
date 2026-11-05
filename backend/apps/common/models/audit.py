import uuid

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.exceptions import AuditError, AuditImmutable
from apps.common.models.choices import ActorKind, AuditAction, AuditOutcome, AuditSource


class AuditEventQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise AuditImmutable("Audit events cannot be changed.")

    def delete(self):
        raise AuditImmutable("Audit events cannot be deleted.")


class AuditEvent(models.Model):
    """Unveränderlicher Eintrag: wer hat wann was an welchem Objekt getan.

    Schreiben läuft über `apps.common.services.record`. Die Zeile bleibt nach
    dem Insert stehen. Änderung und Löschung lehnt das Modell ab; ein
    Datenbank-Trigger fängt Zugriffe ab, die am Modell vorbei gehen.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    occurred_at = models.DateTimeField(_("occurred at"), default=timezone.now, db_index=True)

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("actor"),
        related_name="audit_events",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    actor_pk = models.CharField(_("actor id snapshot"), max_length=64, blank=True)
    actor_label = models.CharField(_("actor label"), max_length=255, blank=True)
    actor_kind = models.CharField(
        _("actor kind"),
        max_length=16,
        choices=ActorKind,
        default=ActorKind.SYSTEM,
    )

    action = models.CharField(_("action"), max_length=32, choices=AuditAction, db_index=True)
    verb = models.CharField(_("verb"), max_length=128, db_index=True)

    content_type = models.ForeignKey(
        ContentType,
        verbose_name=_("content type"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    object_pk = models.CharField(_("object id"), max_length=64, blank=True)
    object_repr = models.CharField(_("object"), max_length=255, blank=True)
    content_object = GenericForeignKey("content_type", "object_pk")

    changes = models.JSONField(_("changes"), default=list, blank=True)
    extra = models.JSONField(_("extra"), default=dict, blank=True)

    outcome = models.CharField(
        _("outcome"),
        max_length=16,
        choices=AuditOutcome,
        default=AuditOutcome.SUCCESS,
    )
    message = models.TextField(_("message"), blank=True)

    request_id = models.CharField(_("request id"), max_length=64, blank=True, db_index=True)
    correlation_id = models.CharField(
        _("correlation id"),
        max_length=64,
        blank=True,
        db_index=True,
    )
    ip_address = models.GenericIPAddressField(_("IP address"), null=True, blank=True)
    user_agent = models.CharField(_("user agent"), max_length=512, blank=True)
    http_method = models.CharField(_("HTTP method"), max_length=16, blank=True)
    path = models.CharField(_("path"), max_length=512, blank=True)
    source = models.CharField(
        _("source"),
        max_length=16,
        choices=AuditSource,
        default=AuditSource.SERVICE,
    )

    objects = AuditEventQuerySet.as_manager()

    class Meta:
        verbose_name = _("audit event")
        verbose_name_plural = _("audit events")
        ordering = ["-occurred_at", "-id"]
        indexes = [
            models.Index(
                fields=["content_type", "object_pk", "-occurred_at"],
                name="audit_target_occurred_idx",
            ),
            models.Index(fields=["actor", "-occurred_at"], name="audit_actor_occurred_idx"),
            models.Index(fields=["verb", "-occurred_at"], name="audit_verb_occurred_idx"),
        ]

    def __str__(self):
        when = self.occurred_at.isoformat() if self.occurred_at else ""
        subject = self.object_repr or self.verb
        actor = self.actor_label or self.actor_kind
        return f"{when} {actor} {self.action} {subject}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise AuditImmutable("Audit events cannot be changed.")
        if self.action not in AuditAction.values:
            raise AuditError(f"Unknown audit action: {self.action}")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise AuditImmutable("Audit events cannot be deleted.")
