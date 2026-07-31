from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal


class Contract(models.Model):
    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Sent', 'Sent'),
        ('Signed', 'Signed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    contract_number = models.CharField(max_length=20, unique=True, editable=False)
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='contracts')
    project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, null=True, blank=True, related_name='contracts')
    quotation = models.ForeignKey('quotations.Quotation', on_delete=models.SET_NULL, null=True, blank=True, related_name='contracts')
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True, help_text='Scope of works / project description')
    terms = models.TextField(blank=True, help_text='Contract terms and conditions')
    contract_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    deposit_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('30.00'), help_text='Deposit required as % of contract amount')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')
    client_signature_name = models.CharField(max_length=200, blank=True, help_text='Name of the person signing on behalf of the client')
    client_signature_data = models.TextField(blank=True, help_text='Handwritten signature image (data URI)')
    signed_at = models.DateTimeField(null=True, blank=True)
    owner_signature_name = models.CharField(max_length=200, blank=True, help_text='Name of the company authorised signatory')
    owner_signature_data = models.TextField(blank=True, help_text='Handwritten signature image (data URI)')
    owner_signed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='contracts_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.contract_number

    @property
    def deposit_amount(self):
        return (self.contract_amount * self.deposit_percent) / Decimal('100.00')

    @property
    def balance_amount(self):
        return self.contract_amount - self.deposit_amount

    @property
    def client_signed(self):
        return bool(self.client_signature_name)

    @property
    def owner_signed(self):
        return bool(self.owner_signature_name)

    @property
    def fully_signed(self):
        return self.client_signed and self.owner_signed

    def save(self, *args, **kwargs):
        if not self.contract_number:
            year = self.created_at.year if self.created_at else 2026
            from django.utils import timezone
            year = timezone.now().year
            last = Contract.objects.filter(contract_number__startswith=f'CTR-{year}-').order_by('contract_number').last()
            if last:
                num = int(last.contract_number.split('-')[-1]) + 1
            else:
                num = 1
            self.contract_number = f'CTR-{year}-{num:04d}'
        super().save(*args, **kwargs)

    def mark_client_signed(self, signature_name, signature_data=''):
        from django.utils import timezone
        self.status = 'Signed'
        self.client_signature_name = signature_name
        self.client_signature_data = signature_data
        self.signed_at = timezone.now()
        self.save(update_fields=['status', 'client_signature_name', 'client_signature_data', 'signed_at'])

    def mark_owner_signed(self, signature_name, signature_data=''):
        from django.utils import timezone
        self.owner_signature_name = signature_name
        self.owner_signature_data = signature_data
        self.owner_signed_at = timezone.now()
        if self.client_signed:
            self.status = 'Signed'
            save_fields = ['owner_signature_name', 'owner_signature_data', 'owner_signed_at', 'status']
        else:
            save_fields = ['owner_signature_name', 'owner_signature_data', 'owner_signed_at']
        self.save(update_fields=save_fields)
