from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Material, StockTransaction


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'quantity', 'unit', 'unit_cost', 'supplier', 'reorder_level', 'is_low_stock')
    list_filter = ('category', 'unit')
    search_fields = ('name', 'supplier')
    readonly_fields = ('quantity',)
    list_editable = ('unit_cost',)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        if obj and obj.stock_transactions.exists():
            return False
        return super().has_delete_permission(request, obj)


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ('material', 'transaction_type', 'quantity', 'reference', 'project', 'done_by', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('material__name', 'reference', 'notes')
    date_hierarchy = 'created_at'
    readonly_fields = ('material', 'transaction_type', 'quantity', 'reference', 'notes', 'project', 'done_by', 'created_at')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
