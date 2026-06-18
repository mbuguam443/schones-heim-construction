from django.db import models
from django.conf import settings


class Equipment(models.Model):
    class Category(models.TextChoices):
        EXCAVATORS = 'Excavators', 'Excavators'
        TRUCKS = 'Trucks', 'Trucks'
        MIXERS = 'Mixers', 'Mixers'
        GENERATORS = 'Generators', 'Generators'
        COMPRESSORS = 'Compressors', 'Compressors'
        OTHER = 'Other', 'Other'

    class Status(models.TextChoices):
        AVAILABLE = 'Available', 'Available'
        IN_USE = 'In Use', 'In Use'
        UNDER_MAINTENANCE = 'Under Maintenance', 'Under Maintenance'

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER)
    registration_number = models.CharField(max_length=100, unique=True)
    purchase_date = models.DateField(null=True, blank=True)
    maintenance_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.registration_number})'

    def cancel(self):
        self.is_active = False
        self.save(update_fields=['is_active'])

    def restore(self):
        self.is_active = True
        self.save(update_fields=['is_active'])


class EquipmentUsageLog(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='usage_logs')
    project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, null=True, blank=True)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    hours_used = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f'{self.equipment} - {self.start_date}'


class MaintenanceRecord(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='maintenance_records')
    maintenance_date = models.DateField()
    description = models.TextField()
    cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    performed_by = models.CharField(max_length=200, blank=True)
    next_maintenance_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-maintenance_date']

    def __str__(self):
        return f'{self.equipment} - {self.maintenance_date}'
