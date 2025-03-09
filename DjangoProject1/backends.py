from django.contrib.auth.backends import BaseBackend # Import Django Backend management module
from candidate.models import Application # Import the Application Model
from employee.models import Employee # Import the Employee Model
################################################################################################################

#This backend manages all the login systems
class GlobalAuthBackend(BaseBackend):

    # Global Authentication Method
    def authenticate(self, request, application_number=None, employee_id=None, password=None, **kwargs):

        # Candidates login system
        if application_number: # If an application number is received, the candidate login system is selected

            try: # Login attempt with the received credentials
                application = Application.objects.get(application_number=application_number) # Try to get the application corresponding to the received application_number
                if application.check_password(password): # If the application exists and the received password is valid ...
                    return application # Return the application

            except Application.DoesNotExist: # The application doesn't exist
                pass

        # Employees login system
        if employee_id: #If an employee id is received, the employee login system is selected

            try: # Login attempt with the received credentials
                employee = Employee.objects.get(employee_email=employee_id) # Try to get the employee corresponding to the received employee id
                if employee.check_password(password): # If the employee exists and the received password is valid ...
                    return employee # Return the corresponding employee

            except Employee.DoesNotExist: # The application doesn't exist
                pass

        return None # Return nothing if the credentials are incorrect

    # Global User Selection Method
    def get_user(self, id):

        try: # Application Retrieving attempt
            return Application.objects.get(pk=id) # Try to return the application corresponding to the ID

        except Application.DoesNotExist: # The application doesn't exist or the ID is not an application's number
            pass

        try: # Employee Retrieving attempt
            return Employee.objects.get(pk=id) # Try to return the employee corresponding to the ID

        except Employee.DoesNotExist: # The employee doesn't exist or the ID is not an employee's id
            pass

        return None # Return nothing if the id doesn't correspond to an application's number nor an employee's id

