from django import forms
from .models import Contract


class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = ('client', 'project', 'quotation', 'title', 'description', 'terms',
                  'contract_amount', 'deposit_percent', 'start_date', 'end_date',
                  'status', 'notes')
        widgets = {
            'client': forms.Select(attrs={'class': 'form-select'}),
            'project': forms.Select(attrs={'class': 'form-select'}),
            'quotation': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Construction of 4-Bedroom Residence - Karen'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Scope of works...'}),
            'terms': forms.Textarea(attrs={'class': 'form-control', 'rows': 8, 'placeholder': 'Terms and conditions of the agreement...'}),
            'contract_amount': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'deposit_percent': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '100', 'step': '1'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['project'].queryset = self.fields['project'].queryset.select_related('client')
        self.fields['project'].label_from_instance = lambda obj: f"{obj.name} ({obj.client.full_name if obj.client else 'No client'})"


class ContractSignForm(forms.Form):
    signature_name = forms.CharField(max_length=200, label='Signatory name (on behalf of client)',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full name of signatory'}))
