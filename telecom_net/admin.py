from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django import forms
from .models import InfrastructureObject, CableRoute, ObjectHistory

class InfrastructureObjectForm(forms.ModelForm):
    class Meta:
        model = InfrastructureObject
        fields = "__all__"

class ObjectHistoryInline(admin.TabularInline):
    model = ObjectHistory
    extra = 0
    fields = ['action', 'description', 'performed_by', 'performed_date']
    readonly_fields = ['performed_date']
    classes = ['collapse']

@admin.register(InfrastructureObject)
class InfrastructureObjectAdmin(admin.ModelAdmin):
    form = InfrastructureObjectForm

    readonly_fields = [
        "select_on_map_button",
        "photo_preview",
        "diagram_preview",
        "created_at",
        "updated_at",
    ]

    fieldsets = [
        ("Основная информация", {
            "fields": [
                "object_id", "name", "object_type", "technology", "status",
            ]
        }),
        ("Географические данные", {
            "fields": [
                "address",
                ("lat", "lng"),
                "select_on_map_button",
            ]
        }),
        ("Технические характеристики", {
            "fields": ["capacity", "free_ports", "parent"]
        }),
        ("Изображения", {
            "fields": [
                "photo", "photo_preview",
                "diagram", "diagram_preview"
            ]
        }),
        ("Даты", {
            "fields": [
                "installation_date", "last_maintenance", "next_maintenance"
            ]
        }),
        ("Примечания", {
            "fields": ["technical_notes", "notes"],
            "classes": ["collapse"]
        }),
        ("Системная информация", {
            "fields": ["is_active", "created_at", "updated_at"],
            "classes": ["collapse"]
        }),
    ]

    inlines = [ObjectHistoryInline]

    def select_on_map_button(self, obj=None):
        """
        Возвращает HTML кнопки, которая открывает modal с iframe /map-picker/.
        В iframe при клике отправляется postMessage родителю с type='coords_selected'.
        """
        html = """
            <button type="button" class="button" onclick="openMapModal()" style="margin-top:6px;">
                🌍 Выбрать на карте
            </button>

            <div id="mapModal" style="display:none; position:fixed; z-index:99999; left:0; top:0; width:100%; height:100%; background:rgba(0,0,0,0.6); padding-top:40px;">
                <div style="margin:auto; background:white; width:90%; height:80%; border-radius:10px; box-shadow:0 6px 24px rgba(0,0,0,0.2); position:relative;">
                    <span onclick="closeMapModal()" style="position:absolute; right:12px; top:8px; cursor:pointer; font-size:26px;">&times;</span>
                    <iframe src="/map-picker/" id="mapPickerFrame" style="width:100%; height:100%; border:none; border-radius:8px;"></iframe>
                </div>
            </div>

            <script>
                function openMapModal() {
                    var el = document.getElementById('mapModal');
                    if (el) el.style.display = 'block';
                }
                function closeMapModal() {
                    var el = document.getElementById('mapModal');
                    if (el) el.style.display = 'none';
                }

                window.addEventListener('message', function(event) {
                    // ожидаем сообщение { type: 'coords_selected', lat: '...', lng: '...' }
                    try {
                        var data = event.data || {};
                        if (data.type === 'coords_selected') {
                            var latInput = document.getElementById('id_lat');
                            var lngInput = document.getElementById('id_lng');
                            if (latInput) latInput.value = data.lat;
                            if (lngInput) lngInput.value = data.lng;
                            // попытка сработать для динамических виджетов
                            if (typeof jQuery !== 'undefined') {
                                jQuery('#id_lat').trigger('change');
                                jQuery('#id_lng').trigger('change');
                            }
                            closeMapModal();
                        }
                    } catch (err) {
                        console.error('map picker message error', err);
                    }
                }, false);
            </script>
        """
        return mark_safe(html)

    select_on_map_button.short_description = "Выбрать на карте"

    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="width:60px;height:60px;border-radius:6px;">', obj.photo.url)
        return "Нет фото"

    def diagram_preview(self, obj):
        if obj.diagram:
            return format_html('<img src="{}" style="width:60px;height:60px;border-radius:6px;">', obj.diagram.url)
        return "Нет схемы"

    class Media:
        # Подключаем статический JS, который при загрузке страницы заполнит поля если в URL есть ?lat=..&lng=..
        js = (
            '/static/telecom_net/js/admin_set_latlng.js',
        )

@admin.register(CableRoute)
class CableRouteAdmin(admin.ModelAdmin):
    readonly_fields = ["route_photo_preview", "created_at", "updated_at"]
    fieldsets = [
        ("Основная информация", {"fields": ["name", "from_object", "to_object"]}),
        ("Характеристики", {"fields": ["cable_type", "route_type", "length", "fiber_count"]}),
        ("Фото", {"fields": ["route_photo", "route_photo_preview", "documentation"]}),
        ("Даты", {"fields": ["installed_date", "tested_date", "test_results"]}),
        ("Примечания", {"fields": ["installation_notes", "technical_specs", "notes"]}),
    ]

    def route_photo_preview(self, obj):
        if obj.route_photo:
            return format_html('<img src="{}" style="width:60px;height:60px;border-radius:6px;">', obj.route_photo.url)
        return "Нет фото"

@admin.register(ObjectHistory)
class ObjectHistoryAdmin(admin.ModelAdmin):
    list_display = ["infrastructure_object", "action", "performed_by", "performed_date"]
    search_fields = ["infrastructure_object__name", "description"]
    list_filter = ["action", "performed_date"]
