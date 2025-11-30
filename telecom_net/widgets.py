from django.forms.widgets import TextInput
from django.utils.safestring import mark_safe


class LatLngWidget(TextInput):
    template_name = "widgets/latlng_widget.html"

    def __init__(self, attrs=None):
        final_attrs = {"class": "vTextField"}  # чтобы выглядело как обычное поле admin
        if attrs:
            final_attrs.update(attrs)
        super().__init__(final_attrs)

    def render(self, name, value, attrs=None, renderer=None):
        input_html = super().render(name, value, attrs, renderer)

        # добавляем кнопку
        button_html = f"""
        <button type="button" class="button select-map" 
                data-target="{attrs.get('id')}" 
                style="margin-left:10px;">
            🌍 Выбрать на карте
        </button>
        """

        return mark_safe(f"{input_html}{button_html}")
