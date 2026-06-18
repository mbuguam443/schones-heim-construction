from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()


class Material(models.Model):
    class Category(models.TextChoices):
        CEMENT = 'cement', _('Cement')
        SAND = 'sand', _('Sand')
        GRAVEL = 'gravel', _('Gravel')
        STEEL = 'steel', _('Steel')
        PAINT = 'paint', _('Paint')
        TIMBER = 'timber', _('Timber')
        OTHER = 'other', _('Other')

    class Unit(models.TextChoices):
        KG = 'kg', _('Kg')
        BAGS = 'bags', _('Bags')
        PIECES = 'pieces', _('Pieces')
        LITRES = 'litres', _('Litres')
        M3 = 'm3', _('m³')

    name = models.CharField(max_length=200, verbose_name=_('Name'))
    category = models.CharField(
        max_length=20, choices=Category.choices, verbose_name=_('Category')
    )
    quantity = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        verbose_name=_('Quantity'),
    )
    unit = models.CharField(
        max_length=10, choices=Unit.choices, verbose_name=_('Unit')
    )
    unit_cost = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name=_('Unit Cost')
    )
    supplier = models.CharField(
        max_length=200, blank=True, verbose_name=_('Supplier')
    )
    reorder_level = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        verbose_name=_('Reorder Level'),
    )
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Material')
        verbose_name_plural = _('Materials')
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.quantity} {self.unit})'

    @property
    def is_low_stock(self):
        return self.quantity <= self.reorder_level

    @property
    def total_value(self):
        return self.quantity * self.unit_cost

    def cancel(self):
        self.is_active = False
        self.save(update_fields=['is_active'])

    def restore(self):
        self.is_active = True
        self.save(update_fields=['is_active'])


class StockTransaction(models.Model):
    class TransactionType(models.TextChoices):
        IN = 'in', _('In')
        OUT = 'out', _('Out')

    material = models.ForeignKey(
        Material, on_delete=models.CASCADE, related_name='stock_transactions',
        verbose_name=_('Material'),
    )
    transaction_type = models.CharField(
        max_length=3, choices=TransactionType.choices, verbose_name=_('Type')
    )
    quantity = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name=_('Quantity')
    )
    reference = models.CharField(
        max_length=200, blank=True, verbose_name=_('Reference')
    )
    notes = models.TextField(blank=True, verbose_name=_('Notes'))
    project = models.ForeignKey(
        'projects.Project', on_delete=models.CASCADE, null=True, blank=True,
        related_name='stock_transactions', verbose_name=_('Project'),
    )
    done_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='stock_transactions', verbose_name=_('Done By'),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))

    class Meta:
        verbose_name = _('Stock Transaction')
        verbose_name_plural = _('Stock Transactions')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_transaction_type_display()} - {self.material.name} x{self.quantity}'

    def delete(self, *args, **kwargs):
        raise PermissionError(
            _("Stock transactions cannot be deleted. "
              "Create a reversal transaction to correct errors.")
        )
