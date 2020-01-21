from django.contrib import auth
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, LoginView
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import loader
from django.template.defaulttags import register

from datacleansing.utils import get_pre_url
from .backends import CustomBackend
from .forms import CustomPasswordChangeForm, CustomPasswordResetForm, CustomLoginForm, CustomUserCreationForm


class CustomLoginView(LoginView):
    template_name = "authentication/login.html"
    form_class = CustomLoginForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == "POST":
            form_obj = CustomLoginForm(data=self.request.POST)
            if form_obj.is_valid():
                user = auth.authenticate(self.request, username=form_obj.cleaned_data['username'],
                                         password=form_obj.cleaned_data['password'],
                                         backend=CustomBackend)

                if user is not None:
                    auth.login(self.request, user, backend=CustomBackend)
                else:
                    context["form_obj"] = form_obj  # Password incorrect
            else:
                context["form_obj"] = form_obj  # Form is invalid
        else:
            context["form_obj"] = CustomLoginForm()
        return context


@login_required
def password_change(request):
    if request.method == "POST":
        form_obj = CustomPasswordChangeForm(data=request.POST, user=request.user)
        if form_obj.is_valid():
            user = form_obj.save()
            update_session_auth_hash(request, user)
            request.session['success'] = True
            return HttpResponseRedirect("/profile")
        else:
            request.session['success'] = False
            request.session['data'] = form_obj.data
            return HttpResponseRedirect("/profile")
    else:
        return HttpResponseRedirect(get_pre_url(request))


def signup(request):
    """A view that provides necessary input fields for registering new users."""
    template = loader.get_template('authentication/signup.html')
    form = CustomUserCreationForm(request.POST)

    if request.method == "POST":
        if form.is_valid():
            user = None

            if user:
                return HttpResponse(template.render(context={'form_obj': form}, request=request))
            else:
                user = form.save()
                auth.login(request, user, backend='authentication.backends.CustomBackend')
                return HttpResponseRedirect('/')
        else:
            return HttpResponse(template.render(context={'form_obj': form}, request=request))
    else:
        form = CustomUserCreationForm()
    return HttpResponse(template.render(context={'form_obj': form}, request=request))


class CustomPasswordResetView(PasswordResetView):
    template_name = "authentication/reset_pwd.html"
    form_class = CustomPasswordResetForm
    subject_template_name = "authentication/password_reset_subject.txt"
    email_template_name = "authentication/password_reset_email.html"
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
            return
    return render(request, "authentication/reset_pwd.html", {"form_obj": form_obj})


@register.filter
def get_item(dictionary, key):
    res = dictionary.get(key)
    if not res:
        return ""
    else:
        return res
