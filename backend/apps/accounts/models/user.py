from django.contrib.auth.models import AbstractUser as DjangoAbstractUser
from django.contrib.auth.models import UserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.accounts.models.choices import Gender, Salutation
from apps.accounts.models.validators import (
    validate_iso_country,
    validate_language_code,
    validate_phone_number,
    validate_timezone_name,
)


class AccountUserManager(UserManager):
    """User-Manager, der eine E-Mail-Adresse erzwingt und normalisiert."""

    def _create_user_object(self, username, email, password, **extra_fields):
        email = (email or "").strip()
        if not email:
            raise ValueError("The given email must be set")
        return super()._create_user_object(username, email, password, **extra_fields)


class AbstractUser(DjangoAbstractUser):
    """Vollständiges abstraktes Benutzerkonto mit Profil- und Adressdaten.

    Enthält die Auth-Funktionen von Djangos AbstractUser (Benutzername,
    Passwort, Rechte, Gruppen, Staff- und Aktiv-Status) und ergänzt
    persönliche Angaben. Konkrete Projekte erben davon oder nutzen `User`.
    """

    email = models.EmailField(
        _("email address"),
        unique=True,
        error_messages={
            "unique": _("A user with that email address already exists."),
        },
    )
    salutation = models.CharField(
        _("salutation"),
        max_length=16,
        choices=Salutation,
        blank=True,
    )
    title = models.CharField(_("title"), max_length=32, blank=True)
    middle_name = models.CharField(_("middle name"), max_length=150, blank=True)
    preferred_name = models.CharField(_("preferred name"), max_length=150, blank=True)
    gender = models.CharField(
        _("gender"),
        max_length=16,
        choices=Gender,
        blank=True,
    )
    pronouns = models.CharField(_("pronouns"), max_length=64, blank=True)
    date_of_birth = models.DateField(_("date of birth"), blank=True, null=True)
    place_of_birth = models.CharField(_("place of birth"), max_length=150, blank=True)
    nationality = models.CharField(
        _("nationality"),
        max_length=2,
        blank=True,
        validators=[validate_iso_country],
        help_text=_("ISO 3166-1 alpha-2 country code."),
    )
    phone = models.CharField(
        _("phone"),
        max_length=32,
        blank=True,
        validators=[validate_phone_number],
    )
    mobile = models.CharField(
        _("mobile"),
        max_length=32,
        blank=True,
        validators=[validate_phone_number],
    )
    website = models.URLField(_("website"), blank=True)
    street = models.CharField(_("street"), max_length=150, blank=True)
    house_number = models.CharField(_("house number"), max_length=16, blank=True)
    address_line2 = models.CharField(_("address line 2"), max_length=150, blank=True)
    postal_code = models.CharField(_("postal code"), max_length=16, blank=True)
    city = models.CharField(_("city"), max_length=150, blank=True)
    region = models.CharField(_("region"), max_length=150, blank=True)
    country = models.CharField(
        _("country"),
        max_length=2,
        blank=True,
        validators=[validate_iso_country],
        help_text=_("ISO 3166-1 alpha-2 country code."),
    )
    bio = models.TextField(_("bio"), blank=True)
    avatar = models.ImageField(
        _("avatar"),
        upload_to="accounts/avatars/%Y/%m/",
        blank=True,
    )
    language = models.CharField(
        _("language"),
        max_length=35,
        blank=True,
        validators=[validate_language_code],
        help_text=_("BCP 47 language code, for example “de” or “en-us”."),
    )
    timezone = models.CharField(
        _("time zone"),
        max_length=64,
        blank=True,
        validators=[validate_timezone_name],
        help_text=_("IANA time zone, for example “Europe/Berlin”."),
    )
    email_verified_at = models.DateTimeField(
        _("email verified at"),
        blank=True,
        null=True,
    )
    phone_verified_at = models.DateTimeField(
        _("phone verified at"),
        blank=True,
        null=True,
    )
    terms_accepted_at = models.DateTimeField(
        _("terms accepted at"),
        blank=True,
        null=True,
    )

    objects = AccountUserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["last_name", "first_name", "username"]
        abstract = True
        indexes = [
            models.Index(fields=["last_name", "first_name"]),
            models.Index(fields=["city"]),
            models.Index(fields=["postal_code"]),
            models.Index(fields=["country"]),
        ]

    def clean(self):
        self._normalize_identity()
        super().clean()
        if self.date_of_birth and self.date_of_birth > timezone.localdate():
            raise ValidationError(
                {"date_of_birth": _("Date of birth cannot be in the future.")},
                code="future_date_of_birth",
            )

    def save(self, *args, **kwargs):
        self._normalize_identity()
        super().save(*args, **kwargs)

    def get_full_name(self):
        parts = (self.title, self.first_name, self.middle_name, self.last_name)
        return " ".join(part.strip() for part in parts if part and part.strip())

    def get_short_name(self):
        return (self.preferred_name or self.first_name or self.get_username()).strip()

    def get_display_name(self):
        if self.preferred_name and self.last_name:
            return f"{self.preferred_name.strip()} {self.last_name.strip()}"
        if self.preferred_name:
            return self.preferred_name.strip()
        return self.get_full_name() or self.get_username()

    def formatted_address(self):
        street = " ".join(
            part for part in (self._text(self.street), self._text(self.house_number)) if part
        )
        locality = " ".join(
            part for part in (self._text(self.postal_code), self._text(self.city)) if part
        )
        lines = [
            street,
            self._text(self.address_line2),
            locality,
            self._text(self.region),
            self._text(self.country),
        ]
        return "\n".join(line for line in lines if line)

    @property
    def age(self):
        if self.date_of_birth is None:
            return None
        today = timezone.localdate()
        years = today.year - self.date_of_birth.year
        if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
            years -= 1
        return years

    @property
    def is_email_verified(self):
        return self.email_verified_at is not None

    @property
    def is_phone_verified(self):
        return self.phone_verified_at is not None

    def __str__(self):
        display = self.get_display_name()
        username = self.get_username()
        if display and display != username:
            return f"{display} ({username})"
        return username

    def _normalize_identity(self):
        self.email = self.__class__.objects.normalize_email(self._text(self.email))
        self.country = self._text(self.country).upper()
        self.nationality = self._text(self.nationality).upper()

    @staticmethod
    def _text(value):
        return (value or "").strip()


class User(AbstractUser):
    """Konkretes, austauschbares Benutzerkonto des Projekts."""

    class Meta(AbstractUser.Meta):
        abstract = False
        swappable = "AUTH_USER_MODEL"
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(email=""),
                name="user_email_present",
            ),
        ]
