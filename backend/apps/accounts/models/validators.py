import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

ISO_COUNTRY_CODE = re.compile(r"^[A-Za-z]{2}$")
LANGUAGE_CODE = re.compile(r"^[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$")
PHONE_NUMBER = re.compile(r"^\+?[0-9][0-9\s()./-]{5,31}$")


def validate_iso_country(value: str) -> None:
    if value and ISO_COUNTRY_CODE.fullmatch(value) is None:
        raise ValidationError(
            _("Enter a two-letter ISO 3166-1 country code."),
            code="invalid_country",
        )


def validate_language_code(value: str) -> None:
    if value and LANGUAGE_CODE.fullmatch(value) is None:
        raise ValidationError(
            _("Enter a language code such as “de” or “en-us”."),
            code="invalid_language",
        )


def validate_phone_number(value: str) -> None:
    if value and PHONE_NUMBER.fullmatch(value) is None:
        raise ValidationError(
            _("Enter a phone number with digits, spaces, and an optional leading +."),
            code="invalid_phone",
        )


def validate_timezone_name(value: str) -> None:
    if not value:
        return
    from zoneinfo import available_timezones

    if value not in available_timezones():
        raise ValidationError(
            _("Enter a valid IANA time zone such as “Europe/Berlin”."),
            code="invalid_timezone",
        )
