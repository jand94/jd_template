from django.middleware.csrf import get_token
from drf_spectacular.utils import OpenApiResponse
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.api.v1.authentication import AccountSessionAuthentication
from apps.accounts.api.v1.permissions import AccountsProfileThrottle, IsActiveAccount
from apps.accounts.api.v1.schema import accounts_schema
from apps.accounts.api.v1.serializers import UserSerializer, UserUpdateSerializer

UNAUTHORIZED = OpenApiResponse(description="Authentication is required or the account is inactive.")


class CsrfView(APIView):
    authentication_classes = [AccountSessionAuthentication]
    permission_classes = [AllowAny]

    @accounts_schema(
        summary="Issue a CSRF cookie",
        description=(
            "Sets the CSRF cookie used by subsequent unsafe requests. Browser "
            "clients call this before register, login, or password reset and "
            "send the token in the X-CSRFToken header."
        ),
        request=None,
        responses={204: None},
        auth=[],
    )
    def get(self, request):
        get_token(request)
        return Response(status=204)


class MeView(APIView):
    authentication_classes = [AccountSessionAuthentication]
    permission_classes = [IsActiveAccount]
    throttle_classes = [AccountsProfileThrottle]

    @accounts_schema(
        summary="Retrieve the signed-in account",
        responses={200: UserSerializer, 401: UNAUTHORIZED, 403: UNAUTHORIZED},
    )
    def get(self, request):
        return Response(UserSerializer(request.user).data)

    @accounts_schema(
        summary="Update the signed-in account",
        description="Changing the email address clears the previous email verification.",
        request=UserUpdateSerializer,
        responses={200: UserSerializer, 400: OpenApiResponse(description="The submitted data is invalid."), 401: UNAUTHORIZED},
    )
    def patch(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data)
