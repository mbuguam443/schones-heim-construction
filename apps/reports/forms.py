from django import forms
from django.utils.translation import gettext_lazy as _


REPORT_TYPE_CHOICES = [
    ('', _('All Reports')),
    ('financial', _('Financial Report')),
    ('project', _('Project Report')),
    ('inventory', _('Inventory Report')),
    ('employee', _('Employee Report')),
]


class ReportFilterForm(forms.Form):
    date_from = forms.DateField(
        label=_('Date From'),
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
    )
    date_to = forms.DateField(
        label=_('Date To'),
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
    )
    project = forms.ChoiceField(
        label=_('Project'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    report_type = forms.ChoiceField(
        label=_('Report Type'),
        choices=REPORT_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    def __init__(self, *args, **kwargs):
        project_choices = kwargs.pop('project_choices', [])
        super().__init__(*args, **kwargs)
        self.fields['project'].choices = [('', _('All Projects'))] + project_choices
