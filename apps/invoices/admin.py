from django.contrib import admin
from .models import Invoice, InvoiceItem, Payment


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    fields = ['description', 'quantity', 'unit', 'unit_price', 'total']
    readonly_fields = ['total']


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ['created_at']
    fields = ['amount', 'payment_date', 'payment_method', 'reference', 'recorded_by']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'client', 'date', 'due_date', 'grand_total', 'amount_paid', 'balance', 'status']
    list_filter = ['status', 'date', 'due_date']
    search_fields = ['invoice_number', 'client__name', 'client__company']
    readonly_fields = ['invoice_number', 'subtotal', 'tax_amount', 'grand_total', 'balance', 'created_at', 'updated_at']
    inlines = [InvoiceItemInline, PaymentInline]
    date_hierarchy = 'date'


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'description', 'quantity', 'unit_price', 'total']
    search_fields = ['description', 'invoice__invoice_number']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'amount', 'payment_date', 'payment_method', 'reference', 'recorded_by']
    list_filter = ['payment_method', 'payment_date']
    search_fields = ['invoice__invoice_number', 'reference']
