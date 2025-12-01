from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.db.models import Q, Count, Sum
from django.http import JsonResponse
import math
from django.shortcuts import render
from .models import InfrastructureObject, CableRoute, ObjectHistory
from .serializers import (
    InfrastructureObjectSerializer, 
    CableRouteSerializer,
    ObjectHistorySerializer
)

def map_picker(request):
    """
    Рендерит страницу map_picker.html — полная карта.
    Используется внутри admin iframe (postMessage) и как отдельная страница.
    """
    return render(request, "map_picker.html")

class InfrastructureObjectViewSet(viewsets.ModelViewSet):
    queryset = InfrastructureObject.objects.all()
    serializer_class = InfrastructureObjectSerializer
    
    def get_queryset(self):
        queryset = InfrastructureObject.objects.select_related('parent').prefetch_related('children')
        
        # Фильтрация по типу объекта
        object_type = self.request.query_params.get('object_type')
        if object_type:
            queryset = queryset.filter(object_type=object_type)
        
        # Фильтрация по технологии
        technology = self.request.query_params.get('technology')
        if technology:
            queryset = queryset.filter(technology=technology)
        
        # Фильтрация по статусу
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Фильтрация по активности
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Поиск
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(object_id__icontains=search) |
                Q(name__icontains=search) |
                Q(address__icontains=search) |
                Q(technical_notes__icontains=search) |
                Q(notes__icontains=search)
            )
        
        return queryset.order_by('object_id')
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Расширенная статистика"""
        stats = {
            'total_objects': InfrastructureObject.objects.count(),
            'active_objects': InfrastructureObject.objects.filter(is_active=True).count(),
            'objects_by_type': InfrastructureObject.objects.values('object_type').annotate(
                count=Count('id')
            ),
            'objects_by_technology': InfrastructureObject.objects.values('technology').annotate(
                count=Count('id')
            ),
            'objects_by_status': InfrastructureObject.objects.values('status').annotate(
                count=Count('id')
            ),
            'total_capacity': InfrastructureObject.objects.aggregate(
                total_capacity=Sum('capacity')
            )['total_capacity'] or 0,
            'total_free_ports': InfrastructureObject.objects.aggregate(
                total_free_ports=Sum('free_ports')
            )['total_free_ports'] or 0,
            'utilization_rate': round(
                (InfrastructureObject.objects.aggregate(total_free=Sum('free_ports'))['total_free'] or 0) / 
                (InfrastructureObject.objects.aggregate(total_cap=Sum('capacity'))['total_cap'] or 1) * 100, 
                2
            ),
        }
        return Response(stats)
    
    @action(detail=True, methods=['get'])
    def connected_routes(self, request, pk=None):
        """Получить связанные кабельные трассы"""
        obj = self.get_object()
        routes = CableRoute.objects.filter(
            Q(from_object=obj) | Q(to_object=obj)
        ).filter(is_active=True)
        serializer = CableRouteSerializer(routes, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """История изменений объекта"""
        obj = self.get_object()
        history = obj.history.all().order_by('-performed_date')
        serializer = ObjectHistorySerializer(history, many=True)
        return Response(serializer.data)


class CableRouteViewSet(viewsets.ModelViewSet):
    queryset = CableRoute.objects.all()
    serializer_class = CableRouteSerializer
    
    def get_queryset(self):
        queryset = CableRoute.objects.select_related('from_object', 'to_object')
        
        # Фильтрация по типу кабеля
        cable_type = self.request.query_params.get('cable_type')
        if cable_type:
            queryset = queryset.filter(cable_type=cable_type)
        
        # Фильтрация по типу прокладки
        route_type = self.request.query_params.get('route_type')
        if route_type:
            queryset = queryset.filter(route_type=route_type)
        
        # Фильтрация по активности
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('name')


class ObjectHistoryViewSet(viewsets.ModelViewSet):
    queryset = ObjectHistory.objects.all()
    serializer_class = ObjectHistorySerializer


# Улучшенная функция проверки подключения
def calculate_distance(lat1, lng1, lat2, lng2):
    """Расчет расстояния между двумя точками (упрощенный)"""
    R = 6371  # Радиус Земли в км
    
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    
    a = (math.sin(dlat/2) * math.sin(dlat/2) + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(dlng/2) * math.sin(dlng/2))
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    return distance * 1000  # в метрах


@api_view(['GET'])
def check_connection(request):
    """Улучшенная проверка возможности подключения"""
    address = request.GET.get('address', '')
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    
    # Если координаты не предоставлены, используем фиктивные
    if not lat or not lng:
        lat = 38.56  # Душанбе
        lng = 68.78
    
    try:
        lat = float(lat)
        lng = float(lng)
        
        # Находим все активные объекты со свободными портами
        all_objects = InfrastructureObject.objects.filter(
            is_active=True, 
            free_ports__gt=0
        )
        
        # Рассчитываем расстояние до каждого объекта
        objects_with_distance = []
        for obj in all_objects:
            distance = calculate_distance(lat, lng, obj.lat, obj.lng)
            objects_with_distance.append({
                'object': obj,
                'distance': distance
            })
        
        # Сортируем по расстоянию и берем ближайшие
        nearest_objects = sorted(objects_with_distance, key=lambda x: x['distance'])[:10]
        
        # Фильтруем только в радиусе 2 км
        nearest_in_range = [obj for obj in nearest_objects if obj['distance'] <= 2000]
        
        available = len(nearest_in_range) > 0
        technology = None
        message = ""
        
        if available:
            # Определяем доступные технологии
            technologies = set(obj['object'].technology for obj in nearest_in_range if obj['object'].technology)
            if technologies:
                technology = 'GPON' if 'gpon' in technologies else 'ADSL' if 'adsl' in technologies else 'Ethernet'
            
            nearest_obj = nearest_in_range[0]
            message = (f"✅ Подключение ВОЗМОЖНО\n"
                      f"Ближайшая точка: {nearest_obj['object'].name}\n"
                      f"Расстояние: {int(nearest_obj['distance'])} м\n"
                      f"Технология: {technology}\n"
                      f"Свободных портов: {nearest_obj['object'].free_ports}")
        else:
            if nearest_objects:
                nearest_obj = nearest_objects[0]
                message = (f"❌ Подключение НЕВОЗМОЖНО в данном месте\n"
                          f"Ближайшая точка: {nearest_obj['object'].name}\n"
                          f"Расстояние: {int(nearest_obj['distance'])} м\n"
                          f"Требуется прокладка кабеля")
            else:
                message = "❌ В радиусе 5 км нет точек подключения"
        
        result_data = {
            'address': address,
            'status': 'available' if available else 'unavailable',
            'technology': technology,
            'nearest_objects': InfrastructureObjectSerializer(
                [obj['object'] for obj in nearest_in_range], 
                many=True
            ).data,
            'distances': {obj['object'].id: int(obj['distance']) for obj in nearest_in_range},
            'message': message,
            'available': available
        }
        
        return Response(result_data)
        
    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'Ошибка при проверке подключения'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def map_data(request):
    """Данные для карты с фильтрацией"""
    object_type = request.GET.get('object_type')
    technology = request.GET.get('technology')
    
    infrastructure_objects = InfrastructureObject.objects.filter(is_active=True)
    cable_routes = CableRoute.objects.filter(is_active=True)
    
    if object_type:
        infrastructure_objects = infrastructure_objects.filter(object_type=object_type)
    if technology:
        infrastructure_objects = infrastructure_objects.filter(technology=technology)
    
    data = {
        'infrastructure_objects': InfrastructureObjectSerializer(infrastructure_objects, many=True).data,
        'cable_routes': CableRouteSerializer(cable_routes, many=True).data
    }
    
    return Response(data)


@api_view(['GET'])
def search(request):
    """Улучшенный поиск"""
    query = request.GET.get('q', '')
    
    if not query or len(query) < 2:
        return Response({'error': 'Слишком короткий запрос'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Поиск по объектам инфраструктуры
    objects = InfrastructureObject.objects.filter(
        Q(object_id__icontains=query) |
        Q(name__icontains=query) |
        Q(address__icontains=query) |
        Q(technical_notes__icontains=query)
    ).filter(is_active=True)[:20]
    
    # Поиск по кабельным трассам
    routes = CableRoute.objects.filter(
        Q(name__icontains=query) |
        Q(installation_notes__icontains=query) |
        Q(notes__icontains=query)
    ).filter(is_active=True)[:10]
    
    result = {
        'infrastructure_objects': InfrastructureObjectSerializer(objects, many=True).data,
        'cable_routes': CableRouteSerializer(routes, many=True).data,
        'total_results': objects.count() + routes.count()
    }
    
    return Response(result)
