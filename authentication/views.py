from django.shortcuts import render
from django.http import *
from django.contrib import auth, messages
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .backends import CustomBackend
from .forms import CustomPasswordChangeForm, CustomPasswordResetForm, PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView, PasswordResetView
from django.template.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.template.defaulttags import register
from django.template import loader
from .models import *
from django.views.decorators.csrf import csrf_exempt


MSG_SUCCESS = "User registration succeed"
MSG_FAIL_EMAIL = "Email {} has been used"
MSG_FAIL_CERTI = "Certificate {} has been used"
MSG_FAIL_FILL = "Please fill in {}."


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


def signup(request):
    """A view that provides necessary input fields for registering new users."""
    template = loader.get_template('authentication/signup.html')
    specializations = Specialization.objects.all()
    spec_groups = {}
    for specialization in specializations:
        groups = CustomGroup.objects.filter(main_group=specialization).values()
        spec_groups[specialization.id] = [group for group in groups]

    context = {
        'specializations': specializations,
        'groups': spec_groups,
        'login_user': request.user,
    }

    # deal with messages passed from the previous page
    obj = request.session.pop('obj', False)
    if obj:
        context['obj'] = obj

    success = request.session.pop('success', False)
    if success:
        messages.success(request, success)

    fail = request.session.pop('error', False)
    if fail:
        messages.add_message(request, messages.ERROR, message=fail, extra_tags="danger")
    return HttpResponse(template.render(context=context, request=request))


@csrf_exempt
def add_user(request):
    """A view that tries to create new user with POST data and pass messages to the next page with session."""
    next = "signup"

    def check(field):
        if field not in request.POST or request.POST[field] == "":
            request.session['error'] = MSG_FAIL_FILL.format(field)
            request.session['obj'] = request.POST
            return False
        return True
    if request.method == "POST":
        # if any of the necessary fields is empty, return error message
        fields = ['username', 'certificate', 'email', 'specialization', 'group']
        for field in fields:
            if not check(field):
                return HttpResponseRedirect(next)

        username = request.POST["username"]
        certificate = request.POST["certificate"]
        email = request.POST["email"]
        group = CustomGroup.objects.get(id=request.POST["group"])
        user = None
        try:
            # if a user with the same email has been created
            user = CustomUser.objects.get(email=email)
            request.session['error'] = MSG_FAIL_EMAIL.format(email)
        except Exception:
            pass

        try:
            # if a user with the same certificate has been created
            user = CustomUser.objects.get(certificate=certificate)
            request.session['error'] = MSG_FAIL_CERTI.format(certificate)
        except Exception:
            pass

        if user:
            request.session['obj'] = request.POST
            return HttpResponseRedirect(next)
        else:
            CustomUser.objects.create_user(email=email, certificate=certificate, username=username,
                                           group=group, password="123456")
            request.session['success'] = MSG_SUCCESS
            return HttpResponseRedirect(next)
    else:
        return HttpResponse("Request method is not allowed.")


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