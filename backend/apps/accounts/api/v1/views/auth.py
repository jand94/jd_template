from django.contrib.auth import logout, update_session_auth_hash
from django.core.exceptions import ValidationError as DjangoValidationError
from drf_spectacular.utils import OpenApiResponse
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.api.v1.authentication import AccountSessionAuthentication
from apps.accounts.api.v1.permissions import (
    AccountsAuthThrottle,
    AccountsPasswordChangeThrottle,
    AccountsRegisterThrottle,
    AccountsResetThrottle,
    IsActiveAccount,
)
from apps.accounts.api.v1.schema import accounts_schema
from apps.accounts.api.v1.serializers import (
    LoginSerializer,
    PasswordChangeSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetSerializer,
    RegisterSerializer,
    UserSerializer,
)
from apps.accounts.exceptions import InvalidCredentials, InvalidPasswordReset
from apps.accounts.services import (
    authenticate_user,
    change_password,
    request_password_reset,
)

AUTH_ERROR = OpenApiResponse(description="The submitted data is invalid.")
UNAUTHORIZED = OpenApiResponse(
    description="Authentication is required or the credentials are invalid."
)


class AccountAuthView(APIView):
    authentication_classes = [AccountSessionAuthentication]
    permission_classes = [AllowAny]


class RegisterView(AccountAuthView):
    throttle_classes = [AccountsRegisterThrottle]

    @accounts_schema(
        summary="Register an account",
        description="Creates an active account, accepts the terms, and starts a session.",
        request=RegisterSerializer,
        responses={201: UserSerializer, 400: AUTH_ERROR},
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = serializer.save()
        except DjangoValidationError as exc:
            raise ValidationError(
                exc.message_dict if hasattr(exc, "message_dict") else exc.messages
            ) from exc
        authenticate_user(
            username=user.get_username(),
            password=serializer.validated_data["password"],
            request=request,
        )
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(AccountAuthView):
    throttle_classes = [AccountsAuthThrottle]

    @accounts_schema(
        summary="Log in",
        description=(
            "Checks the password and starts a session. Unknown usernames, wrong "
            "passwords, and inactive accounts all receive the same 401 response."
        ),
        request=LoginSerializer,
        responses={200: UserSerializer, 400: AUTH_ERROR, 401: UNAUTHORIZED},
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = authenticate_user(request=request, **serializer.validated_data)
        except InvalidCredentials as exc:
            raise AuthenticationFailed("Invalid username or password.") from exc
        return Response(UserSerializer(user).data)


class LogoutView(AccountAuthView):
    permission_classes = [AllowAny]

    @accounts_schema(
        summary="Log out",
        description="Ends the current session.",
        request=None,
        responses={204: None},
    )
    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordChangeView(AccountAuthView):
    permission_classes = [IsActiveAccount]
    throttle_classes = [AccountsPasswordChangeThrottle]

    @accounts_schema(
        summary="Change password",
        request=PasswordChangeSerializer,
        responses={204: None, 400: AUTH_ERROR, 401: UNAUTHORIZED},
    )
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            change_password(
                request.user,
                current_password=serializer.validated_data["current_password"],
                new_password=serializer.validated_data["password"],
            )
        except InvalidCredentials as exc:
            raise ValidationError(
                {"current_password": "The current password is incorrect."}
            ) from exc
        except DjangoValidationError as exc:
            raise ValidationError({"password": list(exc.messages)}) from exc
        update_session_auth_hash(request, request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordResetView(AccountAuthView):
    throttle_classes = [AccountsResetThrottle]

    @accounts_schema(
        summary="Request a password reset",
        description="Always responds the same way, whether or not the email belongs to an account.",
        request=PasswordResetSerializer,
        responses={204: None, 400: AUTH_ERROR},
    )
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_password_reset(email=serializer.validated_data["email"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordResetConfirmView(AccountAuthView):
    throttle_classes = [AccountsResetThrottle]

    @accounts_schema(
        summary="Confirm a password reset",
        request=PasswordResetConfirmSerializer,
        responses={204: None, 400: AUTH_ERROR},
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
        except InvalidPasswordReset as exc:
            raise ValidationError(
                {"token": "This password reset link is invalid or has expired."}
            ) from exc
        except DjangoValidationError as exc:
            raise ValidationError({"password": list(exc.messages)}) from exc
        return Response(status=status.HTTP_204_NO_CONTENT)
