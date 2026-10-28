import pytest
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

from apps.api.errors import FAILURE


class BrokenView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        raise RuntimeError("database password")


class FieldErrorView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        raise ValidationError({"email": "Pflichtfeld", "detail": ["Hinweis"]})


@pytest.mark.api
def test_unhandled_exceptions_are_json_without_internals():
    response = BrokenView.as_view()(APIRequestFactory().get("/broken"))

    assert response.status_code == 500
    assert response.data == {"detail": FAILURE}
    assert "password" not in str(response.data)


@pytest.mark.api
def test_validation_errors_use_detail_and_field_lists():
    response = FieldErrorView.as_view()(APIRequestFactory().get("/fields"))

    assert response.status_code == 400
    assert response.data["email"] == ["Pflichtfeld"]
    assert isinstance(response.data["detail"], str)
