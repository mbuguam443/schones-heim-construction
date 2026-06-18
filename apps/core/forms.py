from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from .models import CompanySettings, User, ClientInquiry
from apps.clients.models import Client


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'position', 'profile_picture')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }


class CompanySettingsForm(forms.ModelForm):
    class Meta:
        model = CompanySettings
        fields = '__all__'
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'kra_pin': forms.TextInput(attrs={'class': 'form-control'}),
            'mpesa_number': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_account': forms.TextInput(attrs={'class': 'form-control'}),
            'tawk_to_property_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 123abc'}),
            'tawk_to_widget_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 1a2b3c4d5'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
        }


class UserCreateForm(UserCreationForm):
    client_link = forms.ModelChoiceField(
        queryset=Client.objects.filter(user__isnull=True),
        required=False,
        label='Link to Client',
        help_text='Optional: link this user to an existing unassigned client record',
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'phone', 'position')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].widget = forms.Select(choices=User.Role.choices)
        self.fields['client_link'].queryset = Client.objects.filter(user__isnull=True)

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            client = self.cleaned_data.get('client_link')
            if client:
                client.user = user
                client.save()
        return user


class UserUpdateForm(UserChangeForm):
    password = None

    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'phone', 'position', 'is_active')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].widget = forms.Select(choices=User.Role.choices)
        self.fields['is_active'].label = 'Active'

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user


class UserPasswordResetForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='New Password',
        min_length=8,
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Confirm Password',
    )

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('new_password')
        p2 = cleaned.get('confirm_password')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned


class ClientInquiryForm(forms.ModelForm):
    class Meta:
        model = ClientInquiry
        fields = ('subject', 'message', 'project')
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Question about my project'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Describe your inquiry in detail...'}),
            'project': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        from apps.projects.models import Project
        if self.user and hasattr(self.user, 'client_profile') and self.user.client_profile:
            self.fields['project'].queryset = Project.objects.filter(client=self.user.client_profile)
            self.fields['project'].empty_label = '-- Not project-specific --'
        else:
            self.fields['project'].queryset = Project.objects.none()
            self.fields['project'].empty_label = '-- No projects available --'


class InquiryResponseForm(forms.Form):
    response = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Write your response...'}),
        label='Your Response',
    )
    status = forms.ChoiceField(
        choices=[('in_progress', 'In Progress'), ('resolved', 'Resolved'), ('closed', 'Closed')],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Update Status',
    )
