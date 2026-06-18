from django import forms
from .models import Project, ProjectAssignment, ProjectPhoto, ProjectDocument


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'client', 'description', 'location', 'start_date', 'end_date', 'budget', 'status', 'progress_percent')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }


class ProjectAssignmentForm(forms.ModelForm):
    class Meta:
        model = ProjectAssignment
        fields = ('employee',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].label_from_instance = lambda obj: f"{obj.get_full_name() or obj.username} ({obj.get_role_display()})"


class ProjectPhotoForm(forms.ModelForm):
    class Meta:
        model = ProjectPhoto
        fields = ('project', 'image', 'caption')
        widgets = {
            'caption': forms.TextInput(attrs={'placeholder': 'Optional caption...'}),
        }


class ProjectDocumentForm(forms.ModelForm):
    class Meta:
        model = ProjectDocument
        fields = ('project', 'file', 'description')
        widgets = {
            'description': forms.TextInput(attrs={'placeholder': 'File description...'}),
        }


class ProjectProgressForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('progress_percent',)
        widgets = {
            'progress_percent': forms.NumberInput(attrs={'min': 0, 'max': 100, 'class': 'form-control-range'}),
        }
