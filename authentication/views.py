from django.shortcuts import render
from django.http import *
from django.contrib import auth
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .backends import CustomBackend
from .forms import CustomPasswordChangeForm, CustomPasswordResetForm, PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView, PasswordResetView
from django.template.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.template.defaulttags import register


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


@login_required
def password_change(request):
    if request.method == "POST":
        form_obj = CustomPasswordChangeForm(data=request.POST, user=request.user)
        if form_obj.is_valid():
            new_pwd = request.POST['new_password1']
            user = request.user
            user.set_password(new_pwd)
            user.save()
            request.session['success'] = True
            return HttpResponseRedirect("/profile")
        else:
            request.session['success'] = False
            request.session['data'] = form_obj.data
            return HttpResponseRedirect("/profile")
    return HttpResponseRedirect(request.path)


class CustomPasswordChangeView(PasswordChangeView):
    template_name = "pages/user/profile.html"
    form_class = CustomPasswordChangeForm

    def get_context_data(self, **kwargs):
        context = {}
        if self.request.method == "POST":
            form_obj = CustomPasswordChangeForm(self.request.POST)
            context.update(csrf(self.request))
            if form_obj.is_valid():
                new_pwd = self.request.POST['new_pwd']
                user = self.request.user
                user.set_password(new_pwd)
                user.save()
            else:
                context["form_obj"] = form_obj
        else:
            form_obj = CustomPasswordChangeForm()
            context["form_obj"] = form_obj
        return context


class CustomPasswordResetView(PasswordResetView):
    template_name = "authentication/reset_pwd.html"
    form_class = CustomPasswordResetForm
    subject_template_name = "authentication/password_reset_subject.txt"
    email_template_name = "authentication/password_reset_email.html"
    token_generator = PasswordResetTokenGenerator
    success_url = "authentication/login.html"

    def get_context_data(self, **kwargs):
        if self.request.method == "POST":
            form_obj = CustomPasswordResetForm(self.request.POST)
        else:
            form_obj = CustomPasswordResetForm()
        context = {"form_obj": form_obj}
        return context


def password_forget(request):
    form_obj = CustomPasswordResetForm()
    if request.method == "POST":
        form_obj = CustomPasswordResetForm(request.POST)
        if form_obj.is_valid():
            token = PasswordResetTokenGenerator()
            return
    return render(request, "authentication/reset_pwd.html", {"form_obj": form_obj})

@register.filter
def get_item(dictionary, key):
    res = dictionary.get(key)
    if not res:
        return ""
    else:
        return res