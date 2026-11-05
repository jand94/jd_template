from django.urls import include, path

app_name = "common"

urlpatterns = [
    path("v1/", include("apps.common.api.v1.urls")),
]
