from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    path('accounts/', include('accounts.urls')),
    path('centers/', include('centers.urls')),
    path('groups/', include('groups.urls')),
    path('assignments/', include('assignments.urls')),
    path('progress/', include('progress.urls')),
    path("analytics/", include("analytics.urls")),
    path("billing/", include("billing.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)