from django.contrib import admin
from .models import Equipment, EquipmentUsageLog, MaintenanceRecord


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'registration_number', 'status', 'purchase_date', 'maintenance_date']
    list_filter = ['category', 'status']
    search_fields = ['name', 'registration_number']


@admin.register(EquipmentUsageLog)
class EquipmentUsageLogAdmin(admin.ModelAdmin):
    list_display = ['equipment', 'project', 'assigned_to', 'start_date', 'end_date', 'hours_used']
    list_filter = ['start_date']


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = ['equipment', 'maintenance_date', 'cost', 'performed_by', 'next_maintenance_date']
    list_filter = ['maintenance_date']
