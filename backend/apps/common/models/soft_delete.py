from django.conf import settings
from django.db import models
from django.db.models.base import ModelBase
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.services.context import current_actor


class SoftDeleteQuerySet(models.QuerySet):
    """`delete()` markiert Zeilen, `hard_delete()` entfernt sie."""

    def delete(self):
        count = 0
        for obj in list(self.iterator()):
            deleted, _details = obj.delete()
            count += deleted
        return count, {self.model._meta.label: count}

    def hard_delete(self):
        return super().delete()


class SoftDeleteManager(models.Manager.from_queryset(SoftDeleteQuerySet)):
    """Liefert nur Zeilen, die nicht als gelöscht markiert sind."""

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class AllObjectsManager(models.Manager.from_queryset(SoftDeleteQuerySet)):
    """Liefert auch als gelöscht markierte Zeilen."""


class SoftDeleteModelBase(ModelBase):
    """Setzt den Base-Manager, auch wenn das Kind eine eigene Meta-Klasse hat."""

    def __new__(cls, name, bases, attrs, **kwargs):
        new_class = super().__new__(cls, name, bases, attrs, **kwargs)
        meta = getattr(new_class, "_meta", None)
        if meta is None or meta.abstract or meta.base_manager_name:
            return new_class
        if any(manager.name == "all_objects" for manager in meta.managers):
            meta.base_manager_name = "all_objects"
            meta.__dict__.pop("base_manager", None)
        return new_class


class SoftDeleteModel(models.Model, metaclass=SoftDeleteModelBase):
    """Optionale Löschmarkierung. Die Zeile bleibt stehen.

    `delete()` setzt `deleted_at` und `deleted_by`. `objects` blendet diese
    Zeilen aus, `all_objects` zeigt sie. `restore()` hebt die Markierung auf.
    `hard_delete()` entfernt die Zeile und folgt `on_delete`. Die Markierung
    kaskadiert nicht. Der Base-Manager bleibt `all_objects`, damit
    Fremdschlüssel und die Audit-Spur die markierte Zeile weiter sehen.
    Zusammen mit `AuditedModel` schreibt die Markierung eine Löschung und das
    Wiederherstellen eine eigene Aktion.

    Ein eindeutiges Feld braucht eine bedingte Unique-Constraint, die nur für
    `deleted_at__isnull=True` gilt. Sonst blockiert eine gelöschte Zeile den
    nächsten Wert.
    """

    deleted_at = models.DateTimeField(_("deleted at"), null=True, blank=True, db_index=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("deleted by"),
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    objects = SoftDeleteManager()
    all_objects = AllObjectsManager()

    class Meta:
        abstract = True
        base_manager_name = "all_objects"

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    def delete(self, using=None, keep_parents=False):
        if self.deleted_at is not None:
            return 0, {}
        self.deleted_at = timezone.now()
        actor = current_actor()
        update_fields = ["deleted_at"]
        if actor is not None and getattr(actor, "pk", None):
            self.deleted_by = actor
            update_fields.append("deleted_by")
        if _has_field(self, "updated_at"):
            update_fields.append("updated_at")
        self.save(update_fields=update_fields)
        return 1, {self._meta.label: 1}

    def hard_delete(self, using=None, keep_parents=False):
        return super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        if self.deleted_at is None:
            return self
        self.deleted_at = None
        self.deleted_by = None
        update_fields = ["deleted_at", "deleted_by"]
        if _has_field(self, "updated_at"):
            update_fields.append("updated_at")
        self.save(update_fields=update_fields)
        return self


def _has_field(instance, name):
    return any(field.name == name for field in instance._meta.concrete_fields)
