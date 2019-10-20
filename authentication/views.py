from django.shortcuts import render

# Create your views here.
def login(request):
    template = loader.get_template('pages/tasks.html')
    username = request.POST['username']
    password = request.POST['password']
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        login(user)
        return HttpResponse(template.render(context))
    else:
        return HttpResponseRedirect(request.path_info)

def logout(request):
    logout(user)
    template = loader.get_template('registration/login.html')
    return HttpResponse(template.render(context))

def password_reset(request):
    raise 1