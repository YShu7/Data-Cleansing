from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from pages.helper import *
from authentication.models import *

@login_required
def index(request):
    user = request.user
    if user is not None:
        if user.is_superuser:
            template = loader.get_template('pages/admin.html')
            context = {
                'specs': Specialization.objects.all(),
                'groups': CustomGroup.objects.all(),
            }
            return HttpResponse(template.render(context=context))
        else:
            return HttpResponseRedirect('/')
    else:
        template = loader.get_template('registration/login.html')
        context = {
            'title': 'Log In',
            'error': "Invalid Log In"
        }
    return HttpResponse(template.render(context))


@login_required
@csrf_exempt
def add_user(request):
    if request.method == "POST":
        print(request.POST)
        username = request.POST["username"]
        certificate = request.POST["certificate"]
        email = request.POST["email"]
        if not request.POST["group"]:
            group = CustomGroup.objects.get(id=request.POST["group"])
        else:
            group = None
        if CustomUser.objects.get(email=email):
            return HttpResponse("Email {} has been used".format(email))
        else:
            CustomUser.objects.create_user(email=email, certificate=certificate, username=username,
                                           group=group, password="123456")
        return HttpResponseRedirect('/')
    else:
        return HttpResponse("Request method is not allowed.")


@login_required
def dataset(request):
    template = loader.get_template('pages/dataset.html')
    ids = [i.id for i in VotingData.objects.all()]
    exclude_ids = [i.task.id for i in AssignmentVote.objects.all()]
    for exclude_id in exclude_ids:
        ids.remove(exclude_id)

    voting_data = []
    for id in ids:
        voting_data.append(VotingData.objects.get(id=id))

    for data in voting_data:
        data.answers = Choice.objects.filter(data_id=data.id)
    context = {
        'title': 'Data Set',
        'num_data': Data.objects.count(),
        'data': voting_data,
    }
    return HttpResponse(template.render(context=context))


@login_required
@csrf_exempt
def update(request, question_id):
    if request.method == 'POST':
        data = VotingData.objects.get(id=question_id)
        ans = request.POST["choice"]
        Data.objects.update_or_create(question_text=data.question_text, answer_text=ans, type=data.type)
        data.delete()
    else:
        HttpResponse("Request method is not allowed.")
    return HttpResponseRedirect("/dataset")


def report(request):
    return HttpResponseRedirect('/report')


def log(request):
    return HttpResponseRedirect('/')