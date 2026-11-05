class AuditError(Exception):
    """Basisklasse für Fehler der Audit-Spur."""


class AuditImmutable(AuditError):
    """Ein Audit-Ereignis darf weder geändert noch gelöscht werden."""


class AuditQueryError(AuditError):
    """Ein Filter der Audit-Abfrage ist ungültig."""

    def __init__(self, detail):
        super().__init__(detail)
        self.detail = detail
