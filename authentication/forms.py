from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordResetForm, PasswordChangeForm, \
    AuthenticationForm, SetPasswordForm
from django.utils.translation import gettext, gettext_lazy as _

from .models import CustomGroup


class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email",
                                widget=forms.widgets.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(
        widget=forms.widgets.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'},
                                           render_value=True))

    class Meta:
        model = get_user_model()
        fields = ('email', 'password')


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(label="Email",
                             widget=forms.widgets.EmailInput(attrs={'class': 'form-control'}))
    username = forms.CharField(label="Username", widget=forms.widgets.Input(attrs={'class': 'form-control'}))
    certificate = forms.CharField(label="Certificate", widget=forms.widgets.Input(attrs={'class': 'form-control'}))
    group = forms.ModelChoiceField(label="Group", queryset=CustomGroup.objects.all(),
                                   widget=forms.widgets.Select(attrs={'class': 'form-control'}), required=True)

    password = None
    password1 = forms.CharField(label="Password", min_length=8,
                                widget=forms.widgets.PasswordInput(attrs={'class': 'form-control'},
                                                                       render_value=True))
    password2 = forms.CharField(label="Password Confirmation", min_length=8,
                                widget=forms.widgets.PasswordInput(attrs={'class': 'form-control'},
                                                                   render_value=True))

    class Meta:
        model = get_user_model()
        fields = ('email', 'username', 'certificate', 'password1', 'password2', 'group')


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = get_user_model()
        fields = ('email', 'username', 'certificate', 'group', 'is_admin')


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.widgets.PasswordInput(attrs={'class': 'form-control'}, render_value=True))
    new_password1 = forms.CharField(label="New Password", min_length=8,
                                    widget=forms.widgets.PasswordInput(attrs={'class': 'form-control'},
                                                                       render_value=True),
                                    error_messages={
                                        "required": "Password cannot be empty",
                                        "min_length": "Password should have at least 8 characters."
                                    })
    new_password2 = forms.CharField(label="Confirm New Password", min_length=8,
                                    widget=forms.widgets.PasswordInput(attrs={'class': 'form-control'},
                                                                       render_value=True),
                                    error_messages={
                                        "required": "Password cannot be empty",
                                        "min_length": "Password should have at least 8 characters."
                                    })


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(label="Email",
                             error_messages={
                                 "required": "Email cannot be empty",
                                 "invalid": "Input is invalid email",
                             },
                             widget=forms.widgets.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))


class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update(
            {'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update(
            {'class': 'form-control'})


class CreateGroupForm(forms.ModelForm):
    name = forms.CharField(label="Group Name",
                           widget=forms.widgets.Input(attrs={'class': 'form-control',
                                                             'placeholder': 'Input group name here'}))

    class Meta:
        model = CustomGroup
        fields = ['name']