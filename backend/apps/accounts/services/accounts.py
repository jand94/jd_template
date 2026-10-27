from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from apps.accounts.exceptions import InactiveAccount, InvalidCredentials, InvalidPasswordReset
from apps.accounts.models import User


def register_user(*, username, email, password, terms_accepted, first_name="", last_name=""):
    if not terms_accepted:
        raise ValidationError({"terms_accepted": "You must accept the terms."})
    return User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        terms_accepted_at=timezone.now(),
    )


def authenticate_user(*, username, password, request):
    user = User.objects.filter(username=username).first()
    if user is None or not user.check_password(password):
        raise InvalidCredentials()
    if not user.is_active:
        raise InactiveAccount()
    login(request, user)
    return user


def update_profile(user, data):
    if "email" in data and data["email"] != user.email:
        user.email_verified_at = None
    for field, value in data.items():
        setattr(user, field, value)
    user.full_clean()
    user.save()
    return user


def change_password(user, *, current_password, new_password):
    if not user.check_password(current_password):
        raise InvalidCredentials()
    validate_password(new_password, user)
    user.set_password(new_password)
    user.save(update_fields=["password"])
    return user


def request_password_reset(*, email):
    user = User.objects.filter(email__iexact=email, is_active=True).first()
    if user is None:
        return
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    send_mail(
        subject=f"Reset your {settings.PROJECT_NAME} password",
        message=(
            f"Set a new password with the {settings.API_TITLE}.\n"
            f"uid: {uid}\n"
            f"token: {token}\n"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )


def confirm_password_reset(*, uid, token, new_password):
    user = _user_from_uid(uid)
    if user is None or not default_token_generator.check_token(user, token):
        raise InvalidPasswordReset()
    validate_password(new_password, user)
    user.set_password(new_password)
    user.save(update_fields=["password"])
    return user


def _user_from_uid(uid):
    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        return User.objects.get(pk=user_id)
    except (User.DoesNotExist, ValueError, TypeError, OverflowError):
        return None
