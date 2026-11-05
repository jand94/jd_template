from django.urls import path

from apps.common.api.v1.views import AuditEventDetailView, AuditEventListView

urlpatterns = [
    path("audit/", AuditEventListView.as_view(), name="audit-list"),
    path("audit/<uuid:event_id>/", AuditEventDetailView.as_view(), name="audit-detail"),
]
