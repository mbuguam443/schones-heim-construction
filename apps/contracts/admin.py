from django.contrib import admin
from .models import Contract

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('contract_number', 'title', 'client', 'contract_amount', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('contract_number', 'title', 'client__full_name')
