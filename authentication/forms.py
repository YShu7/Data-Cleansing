from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordResetForm, PasswordChangeForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'certificate', 'group', 'is_admin')


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'certificate', 'group', 'is_admin')


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.widgets.PasswordInput(attrs={'class': 'form-control'}, render_value=True))
    new_password1 = forms.CharField(label="New Password",min_length=8,
                              widget=forms.widgets.PasswordInput(attrs={'class': 'form-control'}, render_value=True),
                              error_messages={
                                  "required": "Password cannot be empty",
                                  "min_length": "Password should have at least 8 characters."
                              })
    new_password2 = forms.CharField(label="Confirm New Password", min_length=8,
                                 widget=forms.widgets.PasswordInput(attrs={'class': 'form-control'}, render_value=True),
                                 error_messages={
                                     "required": "Password cannot be empty",
                                     "min_length": "Password should have at least 8 characters."
                                 })


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(label="Email",
                             error_messages={
                                 "required": "Email cannot be empty",
                                 "invalid": "Input is invalid email",
                             })