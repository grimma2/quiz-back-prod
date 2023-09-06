from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from quiz import settings

urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('api/v1/team/', include('team.urls')),
    path('api/v1/game/', include('game.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
