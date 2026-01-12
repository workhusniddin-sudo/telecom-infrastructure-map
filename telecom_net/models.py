from django.db import models
from django.core.exceptions import ValidationError


class InfrastructureObject(models.Model):
    OBJECT_TYPES = [
        ('olt', 'OLT Станция'),
        ('splice_box', 'Оптическая муфта'),
        ('splitter', 'Сплиттер-бокс'),
        ('switch', 'Коммутатор'),
        ('ats', 'АТС'),
        ('building', 'Дом'),
        ('client', 'Клиентская точка'),
    ]
    
    TECHNOLOGIES = [
        ('gpon', 'GPON'),
        ('adsl', 'ADSL'),
        ('ethernet', 'Оптика'),
        ('hybrid', 'Гибридный'),
    ]

    STATUS_CHOICES = [
        ('active', 'Активный'),
        ('planned', 'Запланированный'),
        ('inactive', 'Неактивный'),
        ('maintenance', 'На обслуживании'),
    ]
    
    object_id = models.CharField(max_length=50, unique=True, verbose_name="ID объекта")
    object_type = models.CharField(max_length=20, choices=OBJECT_TYPES, verbose_name="Тип объекта")
    name = models.CharField(max_length=100, verbose_name="Название")
    address = models.CharField(max_length=200, blank=True, verbose_name="Адрес")
    lat = models.FloatField(verbose_name="Широта")
    lng = models.FloatField(verbose_name="Долгота")
    technology = models.CharField(max_length=20, choices=TECHNOLOGIES, blank=True, verbose_name="Технология")
    capacity = models.IntegerField(default=0, verbose_name="Общая емкость")
    free_ports = models.IntegerField(default=0, verbose_name="Свободные порты")
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Родительский объект")
    
    # Новые поля для изображений
    photo = models.ImageField(upload_to='infrastructure_photos/', blank=True, null=True, verbose_name="Фотография объекта")
    diagram = models.ImageField(upload_to='infrastructure_diagrams/', blank=True, null=True, verbose_name="Схема подключения")
    
    # Дополнительные поля для комментариев
    technical_notes = models.TextField(blank=True, verbose_name="Технические примечания")
    installation_date = models.DateField(blank=True, null=True, verbose_name="Дата установки")
    last_maintenance = models.DateField(blank=True, null=True, verbose_name="Дата последнего обслуживания")
    next_maintenance = models.DateField(blank=True, null=True, verbose_name="Дата следующего обслуживания")
    
    # Существующие поля
    notes = models.TextField(blank=True, verbose_name="Общие примечания")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Статус")
    is_active = models.BooleanField(default=True, verbose_name="Активный")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Объект инфраструктуры"
        verbose_name_plural = "Объекты инфраструктуры"
        ordering = ['object_id']

    def clean(self):
        if self.free_ports > self.capacity:
            raise ValidationError('Свободных портов не может быть больше общей емкости')
        
    def __str__(self):
        return f"{self.object_id} - {self.name}"


class CableRoute(models.Model):
    CABLE_TYPES = [
        ('fiber', 'Оптический кабель'),
        ('copper', 'Медный кабель'),
        ('hybrid', 'Гибридный кабель'),
    ]

    ROUTE_TYPES = [
        ('underground', 'Подземная'),
        ('aerial', 'Воздушная'),
        ('indoor', 'Внутренняя'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Название трассы")
    from_object = models.ForeignKey(InfrastructureObject, on_delete=models.CASCADE, related_name='routes_from')
    to_object = models.ForeignKey(InfrastructureObject, on_delete=models.CASCADE, related_name='routes_to')
    cable_type = models.CharField(max_length=20, choices=CABLE_TYPES, default='fiber', verbose_name="Тип кабеля")
    route_type = models.CharField(max_length=20, choices=ROUTE_TYPES, default='underground', verbose_name="Тип прокладки")
    length = models.IntegerField(verbose_name="Длина (метры)")
    fiber_count = models.IntegerField(default=1, verbose_name="Количество волокон")
    
    # Новые поля для изображений
    route_photo = models.ImageField(upload_to='route_photos/', blank=True, null=True, verbose_name="Фото трассы")
    documentation = models.FileField(upload_to='route_docs/', blank=True, null=True, verbose_name="Документация")
    
    # Дополнительные поля для комментариев
    installation_notes = models.TextField(blank=True, verbose_name="Примечания по установке")
    technical_specs = models.TextField(blank=True, verbose_name="Технические характеристики")
    tested_date = models.DateField(blank=True, null=True, verbose_name="Дата тестирования")
    test_results = models.TextField(blank=True, verbose_name="Результаты тестирования")
    
    # Существующие поля
    installed_date = models.DateField(blank=True, null=True, verbose_name="Дата прокладки")
    notes = models.TextField(blank=True, verbose_name="Общие примечания")
    is_active = models.BooleanField(default=True, verbose_name="Активная")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Кабельная трасса"
        verbose_name_plural = "Кабельные трассы"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.length}м)"


# Дополнительная модель для хранения истории изменений
class ObjectHistory(models.Model):
    ACTION_CHOICES = [
        ('created', 'Создан'),
        ('updated', 'Обновлен'),
        ('maintenance', 'Обслуживание'),
        ('repaired', 'Ремонт'),
    ]
    
    infrastructure_object = models.ForeignKey(InfrastructureObject, on_delete=models.CASCADE, related_name='history')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="Действие")
    description = models.TextField(verbose_name="Описание")
    photo = models.ImageField(upload_to='history_photos/', blank=True, null=True, verbose_name="Фото")
    performed_by = models.CharField(max_length=100, verbose_name="Выполнил")
    performed_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата выполнения")
    
    class Meta:
        verbose_name = "История объекта"
        verbose_name_plural = "История объектов"
        ordering = ['-performed_date']

    def __str__(self):
        return f"{self.infrastructure_object} - {self.action} - {self.performed_date}"