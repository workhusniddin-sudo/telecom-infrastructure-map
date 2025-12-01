from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from telecom_net import views   # <<< ВАЖНО — ДОБАВЛЕНО

urlpatterns = [
    path('admin/', admin.site.urls),

    # API
    path('api/', include('telecom_net.urls')),

    # Главная карта
    path('', TemplateView.as_view(template_name='map.html'), name='map'),

    # <<< ВАЖНО — ДОБАВЛЕНО >>>
    path('map-picker/', views.map_picker, name='map-picker'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
