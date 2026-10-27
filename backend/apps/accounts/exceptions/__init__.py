class AccountError(Exception):
    """Basisklasse für fachliche Fehler des Benutzerkontos."""


class InvalidCredentials(AccountError):
    """Benutzername oder Passwort ist falsch."""


class InactiveAccount(AccountError):
    """Das Konto darf sich nicht anmelden."""


class InvalidPasswordReset(AccountError):
    """Der Link zum Zurücksetzen des Passworts ist ungültig oder abgelaufen."""
