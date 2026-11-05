from django.db import models


class AuditedModel(models.Model):
    """Zeichnet Anlegen, Ändern und Löschen dieses Modells in der Audit-Spur auf.

    `audit_exclude` nennt Felder, die gar nicht erscheinen. Felder mit
    `password`, `secret` oder `token` im Namen werden protokolliert, ihr Wert
    aber als `[redacted]` gespeichert. `updated_at` ist immer ausgenommen.

    Massen-Updates und `-Deletes` über das QuerySet lösen keine Signale aus
    und brauchen einen eigenen `record`-Aufruf.
    """

    audit_exclude = ()

    class Meta:
        abstract = True
