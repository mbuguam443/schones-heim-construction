from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Employee, Attendance, PerformanceNote


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = (
            'user', 'phone', 'position', 'department', 'salary',
            'employment_date', 'emergency_contact', 'emergency_phone',
            'is_active', 'notes',
        )
        widgets = {
            'employment_date': forms.DateInput(attrs={'class': 'flatpickr-date', 'placeholder': 'YYYY-MM-DD'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ('employee', 'date', 'check_in', 'check_out', 'status', 'notes')
        widgets = {
            'date': forms.DateInput(attrs={'class': 'flatpickr-date', 'placeholder': 'YYYY-MM-DD'}),
            'check_in': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'check_out': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }


class PerformanceNoteForm(forms.ModelForm):
    class Meta:
        model = PerformanceNote
        fields = ('employee', 'note', 'rating')
        widgets = {
            'note': forms.Textarea(attrs={'rows': 3}),
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }
