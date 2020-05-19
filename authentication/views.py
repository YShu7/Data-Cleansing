from django.contrib import auth, messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, LoginView, PasswordResetConfirmView
from django.http.response import HttpResponse, HttpResponseRedirect
from django.template import loader

from datacleansing.settings import MSG_SUCCESS_SIGN_UP, MSG_SUCCESS_PWD_CHANGE
from datacleansing.utils import get_pre_url
from .backends import CustomBackend
from .forms import CustomPasswordChangeForm, CustomPasswordResetForm, CustomLoginForm, CustomUserCreationForm, \
    CustomSetPasswordForm


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

            messages.success(request, MSG_SUCCESS_PWD_CHANGE)
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
            user = form.save()
            auth.login(request, user, backend='authentication.backends.CustomBackend')

            messages.success(request, MSG_SUCCESS_SIGN_UP)
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
    from_email = "Data Cleansing Team <noreply@gmail.com>"


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'authentication/password_reset_confirm.html'
    form_class = CustomSetPasswordForm
