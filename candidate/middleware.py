from django.conf import settings # Import Settings Variables
from django.shortcuts import redirect # Import Django Redirect Module
##########################################################################################################################

class LoginRequiredMiddleware: # Authentication Middleware to require authentication to access private pages

    def __init__(self,get_response):
        self.get_response = get_response

    def __call__(self, request):
        protected_path = ['/candidate/','/candidate/hub','/candidate/logout','/candidate/show_file','/candidate/delete','/candidate/update'] # Private Pages List

        if (request.path in protected_path and not request.user.is_authenticated) or (request.path in protected_path and not hasattr(request.user, 'application_number')): # If the user tries to access the candidate private pages and is not authenticated or is logged as an employee ...
            return redirect(settings.LOGIN_URLS[0]) # Redirect to the candidates login page

        return self.get_response(request)