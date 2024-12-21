from django.conf import settings # Import Settings Variables
from django.shortcuts import redirect # Import Django Redirect Module
##########################################################################################################################

class LoginRequiredMiddleware: # Authentication Middleware to require authentication to access private pages

    def __init__(self,get_response):
        self.get_response = get_response

    def __call__(self, request):
        protected_path = ['/employee/','/employee/hub','/employee/logout','/employee/show_file','/employee/status_modification','/employee/offer_applications'] # Private Pages List

        if (request.path in protected_path and not request.user.is_authenticated) or (request.path in protected_path and not hasattr(request.user, 'employee_email')): # If the user tries to access the employee private pages and is not authenticated or is logged as an candidate ...
            return redirect(settings.LOGIN_URLS[1]) # Redirect to the login page

        return self.get_response(request)