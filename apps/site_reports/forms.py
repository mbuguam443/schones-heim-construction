from django import forms
from .models import DailySiteReport, SiteReportPhoto


class DailySiteReportForm(forms.ModelForm):
    class Meta:
        model = DailySiteReport
        fields = ['project', 'date', 'weather', 'workers_present', 'tasks_completed', 'materials_used', 'challenges']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'tasks_completed': forms.Textarea(attrs={'rows': 4}),
            'materials_used': forms.Textarea(attrs={'rows': 3}),
            'challenges': forms.Textarea(attrs={'rows': 3}),
        }


class SiteReportPhotoForm(forms.ModelForm):
    class Meta:
        model = SiteReportPhoto
        fields = ['image', 'caption']
