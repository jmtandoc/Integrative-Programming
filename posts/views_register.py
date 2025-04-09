from django.http import HttpResponse

# Your RegisterView logic here
class RegisterView:
    def dispatch(self, request):
        # Implement the actual logic for registration
        return HttpResponse('Register View Response')
    