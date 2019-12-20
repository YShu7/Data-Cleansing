from django.contrib import admin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import *


class CustomUserAdmin(admin.ModelAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    fields = ('email', 'username', 'certificate', 'group')
    list_display = ('email', 'username', 'certificate', 'group')
    search_fields = ('email', 'username', 'certificate', )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(CustomGroup)
