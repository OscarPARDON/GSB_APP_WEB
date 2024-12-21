from pathlib import Path # Import File Path Management Module
from django.conf import settings # Import Settings Variables
from django.contrib.auth import authenticate, login, logout # Import Django Authentication Modules
from django.http import FileResponse # Import Django HTTP Modules
from django.shortcuts import render, redirect # Shortcut to import some Django Modules
from candidate.models import Application # Import the application model
from visitor.models import Publication # Import the Publication Model
from .forms import EmployeeLoginForm # Import the Login Form
##############################################################################################


def employee_login(request): # This views manages the employee login process

    if request.method == 'POST': # If form data is received ...
        form = EmployeeLoginForm(request.POST)  # Collect the form data

        if form.is_valid(): # Proceed the form data validation, if no problem is detected ...

            # Collect the input values (cleaned)
            employee_id = form.cleaned_data['employee_id'] # Collect the cleaned employee id
            password = form.cleaned_data['password'] # Collect the cleaned password

            # Authentication
            user = authenticate(request, employee_id=employee_id, password=password)
            if user: # If the authentication was successful ...
                login(request, user) # Log the user in
                return redirect('employee_hub') # Redirect to the employees main page
            else: # If the authentication failed ...
                form.add_error(None, "Identifiant ou mot de passe incorrect.") # Send back to the login page with a message

    else: # If no form data is received
        form = EmployeeLoginForm() # Set a New login form

    return render(request, 'employee_login.html', {'form': form}) # Call the login page

def employee_hub(request): # This view displays the employees main page
    posts = Publication.objects.all()  # Retrieve all the Publications in the Database
    return render(request,'employee_hub.html', {'posts': posts}) # Call the main page

def employee_logout(request): # This view log out the employee
    logout(request) # Log out the user
    response = redirect('/') # Set the redirection URL
    response.delete_cookie('sessionid') # Delete the Session Cookie
    return response # Return the response

def offer_applications(request): # This manage all the applications of an offer
    postID = request.GET.get('postID','') # Get the id of the offer in the URL or set to null


    if not (postID and postID.isdigit() and Publication.objects.filter(id=int(postID)).exists()): # If the job offer doesn't exist ...
        return redirect('/employee/hub') # Redirection to the homepage

    applications = Application.objects.filter(post_id=postID).order_by('status') # Get all the applications corresponding to the offer (ordered by status : In review first)
    return render(request,'offer_applications.html', {'applications': applications}) # Call the offer application page

def show_file(request): # The view manages the access to the applications files

    # Collect the values needed for the view
    application_number = request.GET.get('application_number','') # Get the application number
    filename_base = request.GET.get('file','') # Get the requested file's basename

    # Check the value passed in the URL
    if not filename_base or (filename_base != 'cv' and filename_base != 'coverletter'): # If the requested file's basename is not set or does not correspond to any expected value ...
        return redirect('employee_hub') # Redirection to the candidate's main page

    # Initialization and verification of the directory path
    dir_path = Path(settings.STATICFILES_DIRS[0]) / 'files' / application_number # Construction of the path to the application's file directory
    if not dir_path.exists(): # If the directory does not exist or is not accessible ...
        return redirect('employee_hub') # Redirection to the candidate's main page

    # Search the file in the directory
    matching_files = list(dir_path.glob(f"{filename_base}.*"))  # Search for the file that was asked (all extensions)
    if matching_files: # The file is found
        return FileResponse(open(matching_files[0], 'rb')) # Display the file (Read only)
    return redirect('employee_hub') # Redirection to the candidate's main page

def status_modification(request): # This view manages the modification of an application's status

    # Get the values needed for the views
    application_number = request.GET.get('application_number', '')  # Get the candidate's application number in the URL or set null
    new_status = request.GET.get('status', '') # Get the new status in the URL or set null
    if Application.objects.filter(application_number=application_number):
        application = Application.objects.get(application_number=application_number) # Get the application corresponding to the received application number
    else :
        previous_url = request.META.get('HTTP_REFERER', '/employee/hub')  # Get the previous URL (offer applications)
        return redirect(previous_url)  # Return to the offer applications page

    # Check the values and update the application if they are as expected
    if (application and new_status) and new_status.isdigit() and (1 <= int(new_status) <= 3): # If the values are correct ...
        application.status = new_status # Replace the application status with the new one
        application.save() # Save the modifications in the database

    previous_url = request.META.get('HTTP_REFERER', '/employee/hub') # Get the previous URL (offer applications)
    return redirect(previous_url) # Return to the offer applications page

