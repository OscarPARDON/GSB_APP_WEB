from pathlib import Path # Import File Path Management Module
from secrets import token_hex # Import the token generation Module
from django.conf import settings # Import Settings Variables
from django.contrib.auth import authenticate, login, logout # Import Django Authentication Modules
from django.contrib.auth.hashers import make_password # Import the Django password creation function
from django.http import FileResponse # Import Django HTTP Modules
from django.shortcuts import render, redirect, get_object_or_404  # Shortcut to import some Django Modules
from candidate.models import Application # Import the application model
from visitor.models import Publication # Import the Publication Model
from .forms import EmployeeLoginForm, NewEmployeeForm, UpdateEmployeeForm, UpdateSelfForm, \
    NewPublicationForm, UpdatePublicationForm  # Import the Form
from .models import Employee # Import Employee Model
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

                if user.role == "employee": # If the user is an employee ...
                    return redirect('employee_hub') # Redirect to the employees main page
                elif user.role == "admin": # If the user is an admin
                    return redirect('admin_hub') # Redirect to the admin menu

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

    applications = Application.objects.filter(job_publication=postID).order_by('status') # Get all the applications corresponding to the offer (ordered by status : In review first)
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

def admin_hub(request): # This view displays the admin menu
    if request.user.role == "admin": # If the user is an admin ...
        return render(request, 'admin_hub.html') # Call the admin menu
    return redirect('employee_hub') # If the user is not an admin, redirect on the employees hub

def admin_user_management(request): # This view displays the user management page
    if request.user.role == "admin": # If the user is an admin ...
        users = Employee.objects.all().order_by('employee_lastname','employee_firstname') # Get all the users ordered by names
        return render(request, 'user_management.html', {'users': users}) # Call the user management page
    return redirect('employee_hub') # If the user is not an admin, redirect on the employees hub
def employee_delete(request): # This view delete the employee given in the URL

    if request.user.role == "admin": # If the user is an admin ...
        userID = request.GET.get('userID','') # Get the employee id in the URL or nothing if none is given

        if userID and userID.isdigit() and Employee.objects.filter(id=int(userID)).exists(): # If the employee id is valid and exists ...
            user = get_object_or_404(Employee, id=int(userID)) # Get the employee
            if user.id != request.user.id: # The user can't delete himself
                user.delete() # Delete the employee

        return redirect('user_management') # Redirect to the user management page

    return redirect('employee_hub') # If the employee is not an admin, redirect to the employees page

def new_employee(request): # This view is for creating a new employee

    if request.user.role == "admin": # If the user is an admin ...

        if request.method == 'POST': # If form data is received
            form = NewEmployeeForm(request.POST) # Collect the form data

            if form.is_valid(): # Verify and clean the data
                insertion = Employee(  # Prepare the insertion in the database
                    employee_firstname=form.cleaned_data['employee_firstname'],
                    employee_lastname=form.cleaned_data['employee_lastname'],
                    employee_email=form.cleaned_data['employee_email'],
                    role=form.cleaned_data['role'],
                    password=make_password(token_hex(16)), # Creates a token as a temporary password
                )
                insertion.save()  # Save the employee in the users database
                return redirect('user_management') # Redirect to the user management page

        else : # If no data is received
            form = NewEmployeeForm() # Create an empty form
        return render(request,'new_employee_form.html', {'form': form}) # Call the new employee form

    return redirect('employee_hub') # If the user is not an admin, redirect to the employees page

def employee_update(request): # This view enable the edition of an employee

    if request.user.role != "admin": # If the user is not an admin ...
        return redirect('employee_hub') # Redirect to the employees page

    userID = request.GET.get('userID', '') # Collect the employee id in the URL or nothing if none is passed
    employee = get_object_or_404(Employee, id=userID) if userID.isdigit() else None # Get the employee if the id is valid

    if not employee: # If the employee id is not valid ...
        return redirect('user_management') # Redirect to the user management page

    if request.method == 'POST': # If form data is received
        if int(userID) == request.user.id: # If the user is editing himself ...
            form = UpdateSelfForm(request.POST, instance=employee) # Get data of the self edition form
        else :
            form = UpdateEmployeeForm(request.POST, instance=employee) # Get the data of the employee edition form
        if form.is_valid(): # Verify and clean the form data
            form.save() # Update the employee or the user
            return redirect('user_management') # Redirection to the user management page

    else: # If no form data is received
        if int(userID) == request.user.id: # If the user is editing himself ...
            form = UpdateSelfForm(instance=employee) # Create a new self editing post
        else :
            form = UpdateEmployeeForm(instance=employee) # Create a new employee update form

    return render(request, 'update_employee_form.html', {'form': form,'userID': int(userID)}) # Call the update form

def admin_publication_management(request): # This view displays the publication management page
    posts = Publication.objects.all() # Get all the publications
    return render(request, 'publication_management.html', {'posts': posts}) # Call the publication management page

def new_publication(request): # This view enable to create a publication

    if request.user.role == "admin": # If the user is an admin ...

        if request.method == 'POST': # If form data is received ...
            form = NewPublicationForm(request.POST) # Get the form data

            if form.is_valid(): # Verify and clean the data
                insertion = Publication( # Prepare the insertion in the database
                    title=form.cleaned_data['title'],
                    description=form.cleaned_data['description'],
                    created_by=request.user,
                )
                insertion.save()  # Save the publication in the database
                return redirect('publication_management') # Redirect to the publication management page

        else : # If no form data is received ...
            form = NewPublicationForm() # Create an empty publication creation form
        return render(request, 'publication_form.html', {'form': form, 'action': 'new'}) # Call the publication creation form

    return redirect('employee_hub') # If the user is not an admin, redirect to the employees page

def publication_update(request): # This view enables to update a publication

    if request.user.role != "admin": # If the user is not an admin ...
        return redirect('employee_hub') # Redirect to the employees page

    postID = request.GET.get('postID', '') # Get the publication id in the URL or nothing if none is passed
    publication = get_object_or_404(Publication, id=postID) if postID.isdigit() else None # Get the employee if the id is valid

    if not publication: # If the employee id is not valid ...
        return redirect('publication_management') # Redirect to the publication management page

    if request.method == 'POST': # If form data is received ...
        form = UpdatePublicationForm(request.POST, instance=publication) # Get the form data
        if form.is_valid(): # Verify and clean the form data
            form.save() # Update the publication in the database
            return redirect('publication_management') # Redirection to the publication management page

    else: # If no form data is received ...
        form = UpdatePublicationForm(instance=publication) # Get an empty update form
    return render(request, 'publication_form.html', {'form': form, 'action': 'update'}) # Call the publication update form

def delete_publication(request): # This view delete a publication

    if request.user.role == "admin": # If the user is an admin ...

        postID = request.GET.get('postID','') # Get the publication id or nothing if none is passed
        if postID and postID.isdigit() and Publication.objects.filter(id=int(postID)).exists(): # If the id is valid ...
            publication = get_object_or_404(Publication, id=int(postID)) # Get the publication
            publication.delete() # Delete the publication from the database

        return redirect('publication_management') # Redirection to the publication management page

    return redirect('employee_hub') # If the user is not an admin, redirection to the employees page
