from django.shortcuts import render
from django.template import loader
from django.http import *
from .backends import CustomBackend
from django.contrib import auth


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = CustomBackend.authenticate(CustomBackend, request, username=username, password=password)

        if user is not None:
            auth.login(request, user)
            if user.is_admin:
                return HttpResponseRedirect('/admin')
            else:
                return HttpResponseRedirect('/')
        else:
            return render(request, 'authentication/login.html')
    return render(request, 'authentication/login.html')


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('authentication/login')


def password_reset(request):
    new_pwd = request.POST['new_pwd']
    user = request.user
    user.set_password(new_pwd)
    user.save()
    return True