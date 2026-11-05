import pytest
from drf_spectacular.generators import SchemaGenerator


@pytest.mark.unit
def test_audit_schema_resolves_session_auth_and_content_type():
    schema = SchemaGenerator().get_schema(request=None, public=True)
    operation = schema["paths"]["/common/v1/audit/"]["get"]
    content_type = schema["components"]["schemas"]["AuditEvent"]["properties"]["content_type"]

    assert {"sessionAuth": []} in operation["security"]
    assert content_type["type"] == "string"
    assert content_type["nullable"] is True
