import pytest
from django.contrib.auth import get_user_model
from rest_framework import generics, serializers
from rest_framework.permissions import AllowAny
from rest_framework.test import APIRequestFactory

from apps.api.pagination import PagePagination

User = get_user_model()


class NameSerializer(serializers.Serializer):
    username = serializers.CharField()


class NameList(generics.ListAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = NameSerializer
    pagination_class = PagePagination

    def get_queryset(self):
        return User.objects.order_by("username")


@pytest.mark.api
@pytest.mark.django_db
def test_list_responses_use_the_page_envelope():
    for index in range(21):
        User.objects.create_user(f"user-{index:02d}", f"user-{index:02d}@example.com", "password")

    response = NameList.as_view()(APIRequestFactory().get("/names"))

    assert response.status_code == 200
    assert response.data["count"] == 21
    assert len(response.data["results"]) == 20
    assert set(response.data) == {"count", "next", "previous", "results"}
