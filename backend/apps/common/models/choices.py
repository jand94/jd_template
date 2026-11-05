from django.db import models
from django.utils.translation import gettext_lazy as _


class ActorKind(models.TextChoices):
    USER = "user", _("User")
    ANONYMOUS = "anonymous", _("Anonymous")
    SYSTEM = "system", _("System")


class AuditAction(models.TextChoices):
    CREATE = "create", _("Create")
    UPDATE = "update", _("Update")
    DELETE = "delete", _("Delete")
    RESTORE = "restore", _("Restore")
    ACCESS = "access", _("Access")
    LOGIN = "login", _("Login")
    LOGIN_FAILED = "login_failed", _("Login failed")
    LOGOUT = "logout", _("Logout")
    CUSTOM = "custom", _("Custom")


class AuditOutcome(models.TextChoices):
    SUCCESS = "success", _("Success")
    FAILURE = "failure", _("Failure")


class AuditSource(models.TextChoices):
    API = "api", _("API")
    ADMIN = "admin", _("Admin")
    SHELL = "shell", _("Shell")
    TASK = "task", _("Task")
    SIGNAL = "signal", _("Signal")
    SERVICE = "service", _("Service")
