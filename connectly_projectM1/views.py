from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to Connectly!")

class RegisterView:
    # Your view logic here
    pass
