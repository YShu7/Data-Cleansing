import markdown
from django.http.response import HttpResponseRedirect, HttpResponse
from django.shortcuts import loader
from django.template.defaulttags import register
from django.urls import reverse
from django.utils.translation import get_language

from pages.decorators import login_required


@login_required
def index(request):
    user = request.user
    if user.is_superuser or user.is_admin:
        return HttpResponseRedirect(reverse('admin'))

    return HttpResponseRedirect(reverse("user"))


@login_required
def help(request):
    user = request.user
    template = loader.get_template('help/help.html')
    lang = get_language()

    if user.is_superuser:
        base = "pages/admin/base.html"
        filename = "{}/superuser.md".format(lang)
    elif user.is_admin:
        base = "pages/admin/base.html"
        filename = "{}/admin.md".format(lang)
    else:
        base = "pages/user/base.html"
        filename = "{}/user.md".format(lang)

    with open('pages/templates/help/{}'.format(filename), 'r') as myfile:
        data = myfile.read()

    context = {
        'base': base,
        'my_markdown_title': data,
        'my_markdown_content': data,
    }
    return HttpResponse(template.render(context=context, request=request))


@register.filter
def markdownify(text):
    # safe_mode governs how the function handles raw HTML
    return markdown.markdown(text, safe_mode='escape')
