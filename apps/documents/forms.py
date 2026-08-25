from django import forms
from .models import Document, DocumentCategory, CompanyDocument


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['category', 'project', 'title', 'file', 'description', 'version']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class DocumentCategoryForm(forms.ModelForm):
    class Meta:
        model = DocumentCategory
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class CompanyDocumentForm(forms.ModelForm):
    class Meta:
        model = CompanyDocument
        fields = [
            'doc_type', 'title', 'status', 'project',
            'recipient_name', 'recipient_organization', 'recipient_address', 'subject',
            'report_date', 'prepared_by', 'report_period', 'department', 'show_signature',
        ]
        widgets = {
            'recipient_address': forms.Textarea(attrs={'rows': 3}),
            'report_date': forms.DateInput(attrs={'type': 'date'}),
        }
