from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'infrastructure', views.InfrastructureObjectViewSet, basename='infrastructure')
router.register(r'cable-routes', views.CableRouteViewSet, basename='cable-routes')
router.register(r'history', views.ObjectHistoryViewSet, basename='history')

urlpatterns = [
    path('', include(router.urls)),
    path('check-connection/', views.check_connection, name='check-connection'),
    path('map-data/', views.map_data, name='map-data'),
    path('search/', views.search, name='search'),
    
    # Новые endpoints
    path('infrastructure/<int:pk>/connected-routes/', 
         views.InfrastructureObjectViewSet.as_view({'get': 'connected_routes'}), 
         name='connected-routes'),
    path('infrastructure/<int:pk>/history/', 
         views.InfrastructureObjectViewSet.as_view({'get': 'history'}), 
         name='object-history'),
    path('infrastructure/stats/', 
         views.InfrastructureObjectViewSet.as_view({'get': 'stats'}), 
         name='infrastructure-stats'),
     path("map-picker/", views.map_picker, name="map-picker"),
     
]
