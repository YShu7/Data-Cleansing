from django.shortcuts import HttpResponseRedirect

from pages.decorators import login_required


@login_required
def index(request):
    user = request.user
    if user.is_superuser or user.is_admin:
        return HttpResponseRedirect('/admin')
    else:
        return HttpResponseRedirect('/user')