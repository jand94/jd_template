from io import BytesIO

import pytest
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from PIL import Image

from apps.accounts.exceptions import InvalidPasswordReset
from apps.accounts.models import User
from apps.accounts.models.validators import validate_avatar
from apps.accounts.services import confirm_password_reset, update_profile


def _png_bytes(size=(8, 8), color=(255, 0, 0)):
    buffer = BytesIO()
    Image.new("RGB", size, color=color).save(buffer, format="PNG")
    return buffer.getvalue()


@pytest.mark.unit
@pytest.mark.django_db
def test_update_profile_rejects_unknown_fields():
    user = User.objects.create_user("ada", "ada@example.com", "password")

    with pytest.raises(ValidationError) as exc_info:
        update_profile(user, {"is_superuser": True})

    assert "is_superuser" in exc_info.value.message_dict
    user.refresh_from_db()
    assert user.is_superuser is False


@pytest.mark.unit
@pytest.mark.django_db
def test_update_profile_clears_phone_verification_when_phone_changes():
    user = User.objects.create_user("ada", "ada@example.com", "password")
    user.phone = "+491234567890"
    user.phone_verified_at = user.date_joined
    user.save()

    update_profile(user, {"phone": "+49999888777"})

    user.refresh_from_db()
    assert user.phone == "+49999888777"
    assert user.phone_verified_at is None


@pytest.mark.unit
@pytest.mark.django_db
def test_confirm_password_reset_rejects_inactive_accounts():
    user = User.objects.create_user("ada", "ada@example.com", "a-long-password-99")
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    user.is_active = False
    user.save(update_fields=["is_active"])

    with pytest.raises(InvalidPasswordReset):
        confirm_password_reset(uid=uid, token=token, new_password="another-long-password-99")


@pytest.mark.unit
def test_validate_avatar_rejects_oversized_and_non_image_files():
    huge = SimpleUploadedFile(
        "huge.png",
        b"x" * (2 * 1024 * 1024 + 1),
        content_type="image/png",
    )
    with pytest.raises(ValidationError) as size_error:
        validate_avatar(huge)
    assert size_error.value.error_list[0].code == "avatar_too_large"

    wrong_type = SimpleUploadedFile("note.txt", b"hello", content_type="text/plain")
    with pytest.raises(ValidationError):
        validate_avatar(wrong_type)


@pytest.mark.unit
def test_validate_avatar_accepts_small_png():
    upload = SimpleUploadedFile("ok.png", _png_bytes(), content_type="image/png")
    validate_avatar(upload)
