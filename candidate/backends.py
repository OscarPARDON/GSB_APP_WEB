from django.contrib.auth.backends import BaseBackend # Import Django authentication backend module
from .models import Application # Import the application model
##################################################################################################

class ApplicationAuthBackend(BaseBackend): # Authentication backend for the candidate login system

    # Main authentication function
    def authenticate(self, request, application_number=None, password=None, **kwargs):

        try: # Trying to get the application and checking the password
            application = Application.objects.get(application_number=application_number) # Get the application corresponding to the received application number if it exists
            if application.check_password(password): # If the application number exists, check if the received password is correct
                return application # The password is correct, return the application from the database

        except Application.DoesNotExist: # The application number received does not correspond to any application
            return None # Return nothing

        return None # The application number or the password is incorrect : Return nothing

    def get_user(self, application_number): # Function to get the application corresponding the application number

        try: # Try to get the application corresponding to the application number
            return Application.objects.get(pk=application_number) # Check in the Database

        except Application.DoesNotExist: # The application number does not correspond to any application
            return None # Return nothing

