from django.contrib import admin
from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'company_name', 'email', 'phone', 'created_at')
    search_fields = ('full_name', 'company_name', 'email', 'phone')
    list_filter = ('created_at',)
