from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal


class Quotation(models.Model):
    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Sent', 'Sent'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
        ('Converted', 'Converted'),
    ]

    quotation_number = models.CharField(max_length=20, unique=True, editable=False)
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='quotations')
    project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, null=True, blank=True, related_name='quotations')
    date = models.DateField()
    expiry_date = models.DateField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('16.00'))
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    notes = models.TextField(blank=True)
    terms_conditions = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quotations_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['quotation_number']),
            models.Index(fields=['status']),
            models.Index(fields=['client']),
        ]

    def __str__(self):
        return self.quotation_number

    def save(self, *args, **kwargs):
        if not self.quotation_number:
            year = self.date.year if self.date else 2024
            last_qtn = Quotation.objects.filter(quotation_number__startswith=f'QTN-{year}-').order_by('quotation_number').last()
            if last_qtn:
                last_num = int(last_qtn.quotation_number.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            self.quotation_number = f'QTN-{year}-{new_num:04d}'
        super().save(*args, **kwargs)

    def calculate_totals(self):
        items = self.items.all()
        self.subtotal = sum(item.total for item in items)
        self.tax_amount = (self.subtotal * self.tax_percent) / Decimal('100.00')
        self.grand_total = self.subtotal + self.tax_amount
        self.save(update_fields=['subtotal', 'tax_amount', 'grand_total'])


class QuotationItem(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=500)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    unit = models.CharField(max_length=50, default='pcs')
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return f"{self.quotation.quotation_number} - {self.description[:50]}"

    def save(self, *args, **kwargs):
        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
