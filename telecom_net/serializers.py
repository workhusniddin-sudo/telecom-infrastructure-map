from rest_framework import serializers
from .models import InfrastructureObject, CableRoute, ObjectHistory


class InfrastructureObjectSerializer(serializers.ModelSerializer):
    object_type_display = serializers.CharField(source='get_object_type_display', read_only=True)
    technology_display = serializers.CharField(source='get_technology_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)

    photo_url = serializers.SerializerMethodField()
    diagram_url = serializers.SerializerMethodField()
    children_count = serializers.SerializerMethodField()

    class Meta:
        model = InfrastructureObject
        fields = [
            'id', 'object_id', 'name', 'object_type', 'object_type_display',
            'technology', 'technology_display', 'status', 'status_display',
            'address', 'lat', 'lng', 'capacity', 'free_ports',
            'parent', 'parent_name',
            'photo', 'photo_url',
            'diagram', 'diagram_url',
            'technical_notes',
            'installation_date',
            'last_maintenance',
            'next_maintenance',
            'notes',
            'is_active',
            'children_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    # Фото объекта
    def get_photo_url(self, obj):
        if obj.photo:
            return obj.photo.url
        return None

    # Файл схемы
    def get_diagram_url(self, obj):
        if obj.diagram:
            return obj.diagram.url
        return None

    # ❗ Исправленный children_count
    def get_children_count(self, obj):
        return InfrastructureObject.objects.filter(parent=obj).count()


class CableRouteSerializer(serializers.ModelSerializer):
    from_object_name = serializers.CharField(source='from_object.name', read_only=True)
    from_object_type = serializers.CharField(source='from_object.object_type', read_only=True)

    to_object_name = serializers.CharField(source='to_object.name', read_only=True)
    to_object_type = serializers.CharField(source='to_object.object_type', read_only=True)

    cable_type_display = serializers.CharField(source='get_cable_type_display', read_only=True)
    route_type_display = serializers.CharField(source='get_route_type_display', read_only=True)

    route_photo_url = serializers.SerializerMethodField()

    class Meta:
        model = CableRoute
        fields = [
            'id', 'name',
            'from_object', 'from_object_name', 'from_object_type',
            'to_object', 'to_object_name', 'to_object_type',
            'cable_type', 'cable_type_display',
            'route_type', 'route_type_display',
            'length', 'fiber_count',
            'route_photo', 'route_photo_url',
            'documentation',
            'installation_notes',
            'technical_specs',
            'installed_date',
            'tested_date',
            'test_results',
            'notes',
            'is_active',
            'created_at', 'updated_at'
        ]

    def get_route_photo_url(self, obj):
        if obj.route_photo:
            return obj.route_photo.url
        return None


class ObjectHistorySerializer(serializers.ModelSerializer):
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = ObjectHistory
        fields = '__all__'

    def get_photo_url(self, obj):
        if obj.photo:
            return obj.photo.url
        return None
