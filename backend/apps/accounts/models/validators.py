import re
from io import BytesIO

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

ISO_COUNTRY_CODE = re.compile(r"^[A-Za-z]{2}$")
LANGUAGE_CODE = re.compile(r"^[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$")
PHONE_NUMBER = re.compile(r"^\+?[0-9][0-9\s()./-]{5,31}$")

AVATAR_MAX_BYTES = 2 * 1024 * 1024
AVATAR_MAX_EDGE = 4096
AVATAR_MAX_PIXELS = AVATAR_MAX_EDGE * AVATAR_MAX_EDGE
AVATAR_CONTENT_TYPES = frozenset(
    {
        "image/jpeg",
        "image/png",
        "image/webp",
    }
)
AVATAR_FORMATS = frozenset({"JPEG", "PNG", "WEBP"})


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


def validate_avatar(value) -> None:
    if not value:
        return

    size = getattr(value, "size", None)
    if size is not None and size > AVATAR_MAX_BYTES:
        raise ValidationError(
            _("Avatar files must be %(limit)s bytes or smaller.") % {"limit": AVATAR_MAX_BYTES},
            code="avatar_too_large",
        )

    content_type = getattr(value, "content_type", None)
    if content_type and content_type not in AVATAR_CONTENT_TYPES:
        raise ValidationError(
            _("Upload a JPEG, PNG, or WebP image."),
            code="invalid_avatar_type",
        )

    from PIL import Image

    previous_max = Image.MAX_IMAGE_PIXELS
    Image.MAX_IMAGE_PIXELS = AVATAR_MAX_PIXELS
    try:
        file_obj = getattr(value, "file", value)
        position = file_obj.tell() if hasattr(file_obj, "tell") else None
        try:
            raw = file_obj.read() if hasattr(file_obj, "read") else value.read()
            image = Image.open(BytesIO(raw))
            image.verify()
            image = Image.open(BytesIO(raw))
            width, height = image.size
            if width > AVATAR_MAX_EDGE or height > AVATAR_MAX_EDGE:
                raise ValidationError(
                    _("Avatar images must be at most %(edge)s pixels on each side.")
                    % {"edge": AVATAR_MAX_EDGE},
                    code="avatar_dimensions",
                )
            if (image.format or "").upper() not in AVATAR_FORMATS:
                raise ValidationError(
                    _("Upload a JPEG, PNG, or WebP image."),
                    code="invalid_avatar_type",
                )
        except Image.DecompressionBombError as exc:
            raise ValidationError(
                _("Avatar images must be at most %(edge)s pixels on each side.")
                % {"edge": AVATAR_MAX_EDGE},
                code="avatar_dimensions",
            ) from exc
        except ValidationError:
            raise
        except Exception as exc:
            raise ValidationError(
                _("Upload a valid JPEG, PNG, or WebP image."),
                code="invalid_avatar",
            ) from exc
        finally:
            if position is not None and hasattr(file_obj, "seek"):
                file_obj.seek(position)
            elif hasattr(file_obj, "seek"):
                file_obj.seek(0)
    finally:
        Image.MAX_IMAGE_PIXELS = previous_max
