import re
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()


class Employee(models.Model):
    class Position(models.TextChoices):
        PROJECT_MANAGER = 'project_manager', _('Project Manager')
        SITE_SUPERVISOR = 'site_supervisor', _('Site Supervisor')
        FOREMAN = 'foreman', _('Foreman')
        MASON = 'mason', _('Mason')
        CARPENTER = 'carpenter', _('Carpenter')
        ELECTRICIAN = 'electrician', _('Electrician')
        PLUMBER = 'plumber', _('Plumber')
        WELDER = 'welder', _('Welder')
        PAINTER = 'painter', _('Painter')
        DRIVER = 'driver', _('Driver')
        LABORER = 'laborer', _('Laborer')
        SECURITY = 'security', _('Security')
        CLEANER = 'cleaner', _('Cleaner')
        ACCOUNTANT = 'accountant', _('Accountant')
        ADMIN = 'admin', _('Admin')
        OTHER = 'other', _('Other')

    class Department(models.TextChoices):
        MANAGEMENT = 'management', _('Management')
        FINANCE = 'finance', _('Finance')
        CONSTRUCTION = 'construction', _('Construction')
        ELECTRICAL = 'electrical', _('Electrical')
        PLUMBING = 'plumbing', _('Plumbing')
        PAINTING = 'painting', _('Painting')
        TRANSPORT = 'transport', _('Transport')
        SECURITY = 'security', _('Security')
        OTHER = 'other', _('Other')

    employee_id = models.CharField(
        max_length=10, unique=True, editable=False, verbose_name=_('Employee ID')
    )
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='employee_profile',
        verbose_name=_('User'),
    )
    phone = models.CharField(max_length=15, verbose_name=_('Phone'))
    position = models.CharField(
        max_length=30, choices=Position.choices, verbose_name=_('Position')
    )
    department = models.CharField(
        max_length=30, choices=Department.choices, verbose_name=_('Department')
    )
    salary = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name=_('Salary')
    )
    employment_date = models.DateField(verbose_name=_('Employment Date'))
    emergency_contact = models.CharField(
        max_length=100, blank=True, verbose_name=_('Emergency Contact')
    )
    emergency_phone = models.CharField(
        max_length=15, blank=True, verbose_name=_('Emergency Phone')
    )
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    notes = models.TextField(blank=True, verbose_name=_('Notes'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Employee')
        verbose_name_plural = _('Employees')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username} ({self.employee_id})'

    def save(self, *args, **kwargs):
        if not self.employee_id:
            last = Employee.objects.select_for_update().order_by('-id').first()
            last_num = 0
            if last and last.employee_id:
                match = re.search(r'(\d+)', last.employee_id)
                if match:
                    last_num = int(match.group(1))
            self.employee_id = f'EMP-{last_num + 1:04d}'
        super().save(*args, **kwargs)


class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = 'present', _('Present')
        ABSENT = 'absent', _('Absent')
        LATE = 'late', _('Late')
        HALF_DAY = 'half_day', _('Half-Day')

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name='attendances',
        verbose_name=_('Employee'),
    )
    date = models.DateField(verbose_name=_('Date'))
    check_in = models.TimeField(blank=True, null=True, verbose_name=_('Check In'))
    check_out = models.TimeField(blank=True, null=True, verbose_name=_('Check Out'))
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PRESENT,
        verbose_name=_('Status'),
    )
    notes = models.TextField(blank=True, verbose_name=_('Notes'))
    recorded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='recorded_attendances', verbose_name=_('Recorded By'),
    )

    class Meta:
        verbose_name = _('Attendance')
        verbose_name_plural = _('Attendance Records')
        ordering = ['-date', 'employee__user__first_name']
        unique_together = ['employee', 'date']

    def __str__(self):
        return f'{self.employee} - {self.date} ({self.get_status_display()})'


class PerformanceNote(models.Model):
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name='performance_notes',
        verbose_name=_('Employee'),
    )
    note = models.TextField(verbose_name=_('Note'))
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_('Rating (1-5)'),
    )
    recorded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='recorded_performance', verbose_name=_('Recorded By'),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))

    class Meta:
        verbose_name = _('Performance Note')
        verbose_name_plural = _('Performance Notes')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.employee} - {self.rating}/5 ({self.created_at.date()})'
