from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        PROJECT_MANAGER = 'project_manager', 'Project Manager'
        ACCOUNTANT = 'accountant', 'Accountant'
        SITE_SUPERVISOR = 'site_supervisor', 'Site Supervisor'
        STORE_KEEPER = 'store_keeper', 'Store Keeper'
        EMPLOYEE = 'employee', 'Employee'
        CLIENT = 'client', 'Client'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.EMPLOYEE)
    phone = models.CharField(max_length=15, blank=True)
    position = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_online = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"


class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.recipient}"


class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=200)
    model_name = models.CharField(max_length=100, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.action}"


class CompanySettings(models.Model):
    company_name = models.CharField(max_length=200, default='SCHONES HEIM BUILDERS')
    logo = models.ImageField(upload_to='company/', blank=True, null=True)
    address = models.CharField(max_length=300, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    kra_pin = models.CharField(max_length=20, blank=True)
    mpesa_number = models.CharField(max_length=20, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    bank_account = models.CharField(max_length=100, blank=True)
    tawk_to_property_id = models.CharField(max_length=50, blank=True, help_text='Tawk.to Property ID (e.g. 123abc)')
    tawk_to_widget_id = models.CharField(max_length=50, blank=True, help_text='Tawk.to Widget ID (e.g. 1a2b3c4d5)')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Company Setting'
        verbose_name_plural = 'Company Settings'

    def __str__(self):
        return self.company_name
