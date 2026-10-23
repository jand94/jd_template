import pytest

from apps.api.api.v1.serializers import HealthSerializer


@pytest.mark.unit
def test_health_serializer_accepts_status():
    serializer = HealthSerializer(data={"status": "ok"})

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data == {"status": "ok"}
