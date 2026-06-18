from django.contrib import admin
from .models import Quotation, QuotationItem


class QuotationItemInline(admin.TabularInline):
    model = QuotationItem
    extra = 1
    fields = ['description', 'quantity', 'unit', 'unit_price', 'total']
    readonly_fields = ['total']


@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ['quotation_number', 'client', 'date', 'expiry_date', 'grand_total', 'status', 'created_by']
    list_filter = ['status', 'date', 'created_by']
    search_fields = ['quotation_number', 'client__name', 'client__company']
    readonly_fields = ['quotation_number', 'subtotal', 'tax_amount', 'grand_total', 'created_at', 'updated_at']
    inlines = [QuotationItemInline]
    date_hierarchy = 'date'


@admin.register(QuotationItem)
class QuotationItemAdmin(admin.ModelAdmin):
    list_display = ['quotation', 'description', 'quantity', 'unit_price', 'total']
    search_fields = ['description', 'quotation__quotation_number']
