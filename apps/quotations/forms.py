from django import forms
from django.forms import inlineformset_factory
from .models import Quotation, QuotationItem


class QuotationForm(forms.ModelForm):
    class Meta:
        model = Quotation
        fields = ['client', 'project', 'date', 'expiry_date', 'tax_percent', 'notes', 'terms_conditions', 'status']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'terms_conditions': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-select'}),
            'project': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'tax_percent': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class QuotationItemForm(forms.ModelForm):
    class Meta:
        model = QuotationItem
        fields = ['description', 'quantity', 'unit', 'unit_price', 'total']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Item description'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control form-control-sm item-quantity', 'step': '0.01', 'min': '0.01'}),
            'unit': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'value': 'pcs'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control form-control-sm item-unit-price', 'step': '0.01', 'min': '0'}),
            'total': forms.NumberInput(attrs={'class': 'form-control form-control-sm item-total', 'readonly': True}),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity and quantity <= 0:
            raise forms.ValidationError('Quantity must be greater than zero.')
        return quantity

    def clean_unit_price(self):
        unit_price = self.cleaned_data.get('unit_price')
        if unit_price and unit_price < 0:
            raise forms.ValidationError('Unit price cannot be negative.')
        return unit_price


QuotationItemFormSet = inlineformset_factory(
    Quotation, QuotationItem,
    form=QuotationItemForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)
