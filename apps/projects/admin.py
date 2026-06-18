from django.contrib import admin
from .models import Project, ProjectAssignment, ProjectPhoto, ProjectDocument


class ProjectAssignmentInline(admin.TabularInline):
    model = ProjectAssignment
    extra = 1


class ProjectPhotoInline(admin.TabularInline):
    model = ProjectPhoto
    extra = 1


class ProjectDocumentInline(admin.TabularInline):
    model = ProjectDocument
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', 'status', 'progress_percent', 'budget', 'start_date', 'end_date')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('name', 'client__full_name', 'location')
    inlines = [ProjectAssignmentInline, ProjectPhotoInline, ProjectDocumentInline]


@admin.register(ProjectAssignment)
class ProjectAssignmentAdmin(admin.ModelAdmin):
    list_display = ('project', 'employee', 'assigned_by', 'assigned_at')
    list_filter = ('assigned_at',)


@admin.register(ProjectPhoto)
class ProjectPhotoAdmin(admin.ModelAdmin):
    list_display = ('project', 'caption', 'uploaded_by', 'uploaded_at')


@admin.register(ProjectDocument)
class ProjectDocumentAdmin(admin.ModelAdmin):
    list_display = ('project', 'description', 'uploaded_by', 'uploaded_at')
