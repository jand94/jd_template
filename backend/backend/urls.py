from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

admin.site.site_header = settings.PROJECT_NAME
admin.site.site_title = settings.PROJECT_NAME
admin.site.index_title = settings.PROJECT_NAME

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/', include('apps.api.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('accounts/', include('apps.accounts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
