from drf_spectacular.utils import OpenApiResponse
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, RetrieveAPIView

from apps.common.api.v1.authentication import CommonSessionAuthentication
from apps.common.api.v1.permissions import AuditReadThrottle, CanViewAuditTrail
from apps.common.api.v1.schema import AUDIT_LIST_PARAMETERS, common_schema
from apps.common.api.v1.serializers import AuditEventSerializer
from apps.common.api.v1.services import filter_audit_events
from apps.common.exceptions import AuditQueryError
from apps.common.models import AuditEvent

UNAUTHORIZED = OpenApiResponse(description="Authentication is required.")
FORBIDDEN = OpenApiResponse(
    description="The audit permission is missing or the account is inactive."
)


class AuditEventQueryMixin:
    authentication_classes = [CommonSessionAuthentication]
    permission_classes = [CanViewAuditTrail]
    throttle_classes = [AuditReadThrottle]
    serializer_class = AuditEventSerializer

    def get_queryset(self):
        queryset = AuditEvent.objects.select_related("actor", "content_type")
        try:
            return filter_audit_events(queryset, self.request.query_params)
        except AuditQueryError as exc:
            raise ValidationError({"detail": exc.detail}) from exc


class AuditEventListView(AuditEventQueryMixin, ListAPIView):
    @common_schema(
        operation_id="common_audit_list",
        summary="List audit events",
        description=(
            "Returns the append-only audit trail, newest first. "
            "Requires the permission common.view_auditevent."
        ),
        parameters=AUDIT_LIST_PARAMETERS,
        responses={
            200: AuditEventSerializer(many=True),
            400: OpenApiResponse(description="A filter value is invalid."),
            401: UNAUTHORIZED,
            403: FORBIDDEN,
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class AuditEventDetailView(AuditEventQueryMixin, RetrieveAPIView):
    lookup_field = "id"
    lookup_url_kwarg = "event_id"

    @common_schema(
        operation_id="common_audit_retrieve",
        summary="Retrieve an audit event",
        responses={
            200: AuditEventSerializer,
            401: UNAUTHORIZED,
            403: FORBIDDEN,
            404: OpenApiResponse(description="No audit event with this id exists."),
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
