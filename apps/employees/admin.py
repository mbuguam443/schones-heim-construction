from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Employee, Attendance, PerformanceNote


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'user', 'position', 'department', 'salary', 'is_active', 'created_at')
    list_filter = ('position', 'department', 'is_active', 'employment_date')
    search_fields = ('employee_id', 'user__username', 'user__first_name', 'user__last_name', 'phone')
    date_hierarchy = 'employment_date'
    readonly_fields = ('employee_id', 'created_at', 'updated_at')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'check_in', 'check_out', 'status', 'recorded_by')
    list_filter = ('status', 'date')
    search_fields = ('employee__user__username', 'employee__employee_id', 'employee__user__first_name')
    date_hierarchy = 'date'


@admin.register(PerformanceNote)
class PerformanceNoteAdmin(admin.ModelAdmin):
    list_display = ('employee', 'rating', 'recorded_by', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('employee__user__username', 'employee__employee_id', 'note')
    date_hierarchy = 'created_at'
