from django.shortcuts import redirect
#########################################################################################################

# This global middleware manage the access to the urls
class LoginRequiredMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        public_path = ['/', '/application_success', '/application','/candidate/login','/employee/login', '/candidate/forgot_application_number','/candidate/forgot_password','/candidate/reset_password'] # Publicly accessible paths
        candidate_login_path = '/candidate/login' # The path to the candidates login page
        employee_login_path = '/employee/login' # The path to the employee login page

        # Check if the user is not authenticated and is accessing a private page
        if not request.user.is_authenticated and request.path not in public_path:
            return redirect('/') # Redirection to the visitor homepage

        # If the user is a candidate and is trying to access the employees' side of the chat ...
        if hasattr(request.user,"application_number") and request.path in ["/chat/employee","/chat/new_interview","/chat/delete_interview"]:
            return redirect("/") # Redirect to the main page
        # If the user is an employee and is trying to access the candidates' side of the chat ...
        if hasattr(request.user,"employee_email") and request.path in ["/chat/candidate","/chat/update_interview_status"]:
            return redirect("/") # Redirect to the main page
        # If a user with the role employee try to access admin views
        if request.path in ["/chat/employee","/chat/new_interview","/chat/delete_interview"] and hasattr(request.user,"role") and request.user.role == "employee":
            return redirect("/employee/hub") # Redirect to the employees' main page

        # Bypass the login page if the user is already authenticated
        if (request.path == candidate_login_path) and (request.user.is_authenticated) and (hasattr(request.user, 'application_number')) :
            return redirect('/candidate/hub') # Redirection to the candidates homepage
        elif (request.path == employee_login_path) and (request.user.is_authenticated) and (hasattr(request.user, 'employee_email')) :
            if request.user.role == 'employee' : # If the authenticated user is an employee...
                return redirect('/employee/application_management') # Redirect to the employee homepage
            elif request.user.role == 'admin' : # If the authenticated user is an admin
                return redirect('/employee/hub') # Redirect to the admin homepage

        # Restrict authenticated candidates from accessing the employees section
        if hasattr(request.user, 'application_number'): # If the user is a candidate ...
            if request.path.startswith('/employee/') and request.path != employee_login_path: # And the user tries to access the path of the employees section ...
                return redirect(employee_login_path) # Redirect to the employees login page

        # Restrict authenticated employee from accessing the candidates section
        if hasattr(request.user, 'employee_email'): # If the user is en employee
            if request.path.startswith('/candidate/') and request.path != candidate_login_path: # And the user tries to access the candidates section ...
                return redirect(candidate_login_path) # Redirect to the candidates login page

        # Proceed with the request
        return self.get_response(request)
