from django.contrib import admin
from .models import DailySiteReport, SiteReportPhoto


class SiteReportPhotoInline(admin.TabularInline):
    model = SiteReportPhoto
    extra = 1


@admin.register(DailySiteReport)
class DailySiteReportAdmin(admin.ModelAdmin):
    list_display = ['project', 'date', 'weather', 'workers_present', 'submitted_by']
    list_filter = ['date', 'project']
    search_fields = ['project__name', 'tasks_completed']
    inlines = [SiteReportPhotoInline]
