from rest_framework import serializers

from apps.common.models import AuditEvent


class AuditChangeSerializer(serializers.Serializer):
    field = serializers.CharField()
    old = serializers.JSONField(allow_null=True)
    new = serializers.JSONField(allow_null=True)


class AuditEventSerializer(serializers.ModelSerializer):
    """Lesende Darstellung eines Audit-Ereignisses."""

    changes = AuditChangeSerializer(many=True)
    content_type = serializers.SerializerMethodField()

    class Meta:
        model = AuditEvent
        fields = (
            "id",
            "occurred_at",
            "actor",
            "actor_pk",
            "actor_label",
            "actor_kind",
            "action",
            "verb",
            "content_type",
            "object_pk",
            "object_repr",
            "changes",
            "extra",
            "outcome",
            "message",
            "request_id",
            "correlation_id",
            "ip_address",
            "user_agent",
            "http_method",
            "path",
            "source",
        )
        read_only_fields = fields

    def get_content_type(self, obj: AuditEvent) -> str | None:
        if obj.content_type_id is None:
            return None
        return f"{obj.content_type.app_label}.{obj.content_type.model}"
