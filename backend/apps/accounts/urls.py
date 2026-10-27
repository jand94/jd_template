from django.urls import include, path

urlpatterns = [
    path('v1/', include('apps.accounts.api.v1.urls')),
]
