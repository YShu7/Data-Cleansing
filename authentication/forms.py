from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordResetForm, PasswordChangeForm, \
    AuthenticationForm, SetPasswordForm
from django.utils.translation import gettext, gettext_lazy as _

from .models import CustomGroup


class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(label=_("Email"),
                                widget=forms.widgets.EmailInput(attrs={'class': 'form-control', 'placeholder': _('Email')}))
    password = forms.CharField(
        widget=forms.widgets.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Password')},
                                           render_value=True))

    class Meta:
        model = get_user_model()
        fields = ('email', 'password')


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(label=_("Email"),
                             widget=forms.widgets.EmailInput(attrs={'class': 'form-control'}))
    username = forms.CharField(label=_("Username"), widget=forms.widgets.Input(attrs={'class': 'form-control'}))
    certificate = forms.CharField(label=_("Certificate"), widget=forms.widgets.Input(attrs={'class': 'form-control'}))
    group = forms.ModelChoiceField(label=_("Group"), queryset=CustomGroup.objects.all(),
                                   widget=forms.widgets.Select(attrs={'class': 'form-control'}), required=True)

    password = None
    password1 = forms.CharField(label=_("Password"), min_length=8,
                                widget=forms.widgets.PasswordInput(attrs={'class': 'form-control'}, render_value=True))
    password2 = forms.CharField(label=_("Password Confirmation"), min_length=8,
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
    old_password = forms.CharField(label=_("Old Password"),
                                   widget=forms.widgets.PasswordInput(attrs={'class': 'form-control'},
                                                                      render_value=True))
    new_password1 = forms.CharField(label=_("New Password"), min_length=8,
                                    widget=forms.widgets.PasswordInput(attrs={'class': 'form-control'},
                                                                       render_value=True),
                                    error_messages={
                                        "required": _("Password cannot be empty"),
                                        "min_length": _("Password should have at least 8 characters.")
                                    })
    new_password2 = forms.CharField(label=_("Confirm New Password"), min_length=8,
                                    widget=forms.widgets.PasswordInput(attrs={'class': 'form-control'},
                                                                       render_value=True),
                                    error_messages={
                                        "required": _("Password cannot be empty"),
                                        "min_length": _("Password should have at least 8 characters.")
                                    })


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(label=_("Email"),
                             error_messages={
                                 "required": _("Email cannot be empty"),
                                 "invalid": _("Input is invalid email"),
                             },
                             widget=forms.widgets.EmailInput(attrs={'class': 'form-control', 'placeholder': _('Email')}))


class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update(
            {'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update(
            {'class': 'form-control'})


class CreateGroupForm(forms.ModelForm):
    name = forms.CharField(label=_("Group Name"),
                           widget=forms.widgets.Input(attrs={'class': 'form-control',
                                                             'placeholder': _('Input group name here')}))

    class Meta:
        model = CustomGroup
        fields = ['name']