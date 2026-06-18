from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Material, StockTransaction


class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ('name', 'category', 'quantity', 'unit', 'unit_cost', 'supplier', 'reorder_level')
        widgets = {
            'quantity': forms.NumberInput(attrs={'step': '0.01'}),
            'unit_cost': forms.NumberInput(attrs={'step': '0.01'}),
            'reorder_level': forms.NumberInput(attrs={'step': '0.01'}),
        }


class StockInForm(forms.ModelForm):
    class Meta:
        model = StockTransaction
        fields = ('material', 'quantity', 'project', 'reference', 'notes')
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity <= 0:
            raise forms.ValidationError(_('Quantity must be greater than zero.'))
        return quantity


class StockOutForm(forms.ModelForm):
    class Meta:
        model = StockTransaction
        fields = ('material', 'quantity', 'project', 'reference', 'notes')
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['project'].required = True

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity <= 0:
            raise forms.ValidationError(_('Quantity must be greater than zero.'))
        return quantity
