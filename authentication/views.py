from django.contrib import auth, messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, LoginView
from django.http import *
from django.shortcuts import render
from django.template import loader
from django.template.context_processors import csrf
from django.template.defaulttags import register
from django.utils import log

from .backends import CustomBackend
from .forms import CustomPasswordChangeForm, CustomPasswordResetForm, CustomLoginForm, CustomUserCreationForm

MSG_SUCCESS = "User registration succeed"
MSG_FAIL_EMAIL = "Email {} has been used"
MSG_FAIL_CERTI = "Certificate {} has been used"
MSG_FAIL_FILL = "Please fill in {}."


class CustomLoginView(LoginView):
    template_name = "authentication/login.html"
    form_class = CustomLoginForm

    def get_context_data(self, **kwargs):
        context = {}
        if self.request.method == "POST":
            form_obj = CustomLoginForm(data=self.request.POST)
            context.update(csrf(self.request))
            if form_obj.is_valid():
                user = auth.authenticate(self.request, username=form_obj.cleaned_data['username'],
                                         password=form_obj.cleaned_data['password'],
                                         backend=CustomBackend)

                if user is not None:
                    auth.login(self.request, user, backend=CustomBackend)
                else:
                    print("Password incorrect")
            else:
                context["form_obj"] = form_obj
        else:
            form_obj = CustomLoginForm()
            context["form_obj"] = form_obj
        context['next'] = "/"
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
            request.session['data'] = form_obj.cleaned_data
            return HttpResponseRedirect("/profile")
    return HttpResponseRedirect(request.path)


def signup(request):
    """A view that provides necessary input fields for registering new users."""
    template = loader.get_template('authentication/signup.html')
    form = CustomUserCreationForm(request.POST)
    print(request)
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
    token_generator = auth.tokens.PasswordResetTokenGenerator
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
            token = auth.tokens.PasswordResetTokenGenerator()
            return
    return render(request, "authentication/reset_pwd.html", {"form_obj": form_obj})


@register.filter
def get_item(dictionary, key):
    res = dictionary.get(key)
    if not res:
        return ""
    else:
        return res
