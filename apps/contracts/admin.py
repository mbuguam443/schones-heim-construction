from django.contrib import admin
from .models import Contract

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('contract_number', 'title', 'client', 'contract_amount', 'status', 'client_signed', 'owner_signed', 'created_at')
    list_filter = ('status', 'client_signature_name', 'owner_signature_name')
    search_fields = ('contract_number', 'title', 'client__full_name')
