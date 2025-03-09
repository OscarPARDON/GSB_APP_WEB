import os
from pathlib import Path # Import File Path Management Module
from secrets import token_hex # Import the token generation Module
from django.conf import settings # Import Settings Variables
from django.contrib.auth import authenticate, login, logout # Import Django Authentication Modules
from django.contrib.auth.hashers import make_password # Import the Django password creation function
from django.http import FileResponse, request  # Import Django HTTP Modules
from django.shortcuts import render, redirect, get_object_or_404  # Shortcut to import some Django Modules
from candidate.models import Application # Import the application model
from conversation.models import Message, Thread, Interview
from conversation.views import get_encryption_key, decrypt_message, encrypt_message
from mailing.wsgi import send_email
from visitor.models import Publication # Import the Publication Model
from .forms import EmployeeLoginForm, NewEmployeeForm, UpdateEmployeeForm, UpdateSelfForm, \
    NewPublicationForm, UpdatePublicationForm, EmployeeChangePasswordForm  # Import the Form
from .models import Employee # Import Employee Model
##############################################################################################

# This function deletes all the interviews linked to a thread
def clear_interviews(application_number,employee_id):
    if Thread.objects.filter(candidate_id=application_number,employee_id=employee_id).exists(): # Verify if the thread exists
        thread = Thread.objects.get(candidate_id=application_number, employee_id=employee_id) # Get the thread
        interviews = Interview.objects.filter(thread=thread) # Get the interviews
        if interviews : # If there are interviews in the thread
            for interview in interviews: # Delete all the interviews
                interview.delete()

# This function delete a candidate
def delete_candidate(application_number):
    # Delete the candidate's files and delete the candidate's directory
    dir_path = Path(settings.STATICFILES_DIRS[0]) / 'files' / application_number  # Construction of the path to the candidate's directory
    if dir_path.exists():  # If the directory exist ...
        files_to_remove = ["cv.*", "coverletter.*"]  # List of the files to remove
        for pattern in files_to_remove:  # For all the files in the list ...
            matching_files = list(dir_path.glob(pattern))  # Searching for the file corresponding to the file in the list
            if matching_files:  # If the file is found ...
                os.remove(matching_files[0])  # Delete the file
        os.rmdir(dir_path)  # Delete the candidate's directory

    # Delete the application from the database
    application = get_object_or_404(Application,application_number=application_number)  # Get the application or send 404 error if it's not found in the database

    send_email('deletion_confirmation_email.html', {'job_offer': application.job_publication.title},[application.candidate_mail]) # Send an email to the candidate to inform that his application was deleted

    application.delete()  # Delete the application from the database
    return redirect('/')  # Redirection to the visitor page

###############################################################################################################################

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
                if user.first_connexion == True : # If the user connect for the first time or had his password reset ...
                    return redirect("/employee/change_password") # Redirect to the password change form

                if user.role == "employee": # If the user is an employee ...
                    return redirect('application_management') # Redirect to the employees main page
                elif user.role == "admin" or user.role == "manager": # If the user is an admin
                    return redirect('employee_hub') # Redirect to the admin menu

            else: # If the authentication failed ...
                form.add_error(None, "Identifiant ou mot de passe incorrect.") # Send back to the login page with a message

    else: # If no form data is received
        form = EmployeeLoginForm() # Set a New login form

    return render(request, 'forms/employee_login.html', {'form': form}) # Call the login page

def employee_change_password(request): # The view manages the employees password change

    if request.user.first_connexion == 1: # If the user connects for the first time or had his password reset ...
        user = Employee.objects.get(id=request.user.id) # Get the user

        if request.method == 'POST': # If form data was received ...
            form = EmployeeChangePasswordForm(request.POST, instance=user) # Get the form data and create a user instance

            if form.is_valid(): # If the form data is valid ...
                user.password = make_password(form.cleaned_data['password']) # Set the new password
                user.first_connexion = False # Set the first connection value to NULL for this user
                user.save() # Save the changes in the database

                send_email("confirm_password_change_email.html",{},[user.employee_email]) # Sends an email to confirm the password modification

                return redirect('employee_login') # Redirect to the employees login page
        else : # If no form data was received ...
            form = EmployeeChangePasswordForm(instance=user) # Create an empty form
            return render(request, 'forms/employee_change_password_form.html', {'form': form}) # Call the change password page

    return redirect('/') # If this is not the user first connexion and the user didn't have had his password reset

def application_management(request): # This view displays the employees main page
    posts = Publication.objects.filter(archived=0)  # Retrieve all the Publications in the Database
    return render(request, 'bodies/application_management.html', {'posts': posts}) # Call the main page

def employee_logout(request): # This view log out the employee
    logout(request) # Log out the user
    response = redirect('/') # Set the redirection URL
    response.delete_cookie('sessionid') # Delete the Session Cookie
    return response # Return the response

def offer_applications(request): # This manage all the applications of an offer
    postID = request.GET.get('postID','') # Get the id of the offer in the URL or set to null

    if not (postID and postID.isdigit() and Publication.objects.filter(id=int(postID),archived=0).exists()): # If the job offer doesn't exist ...
        return redirect('application_management') # Redirection to the homepage

    applications = Application.objects.filter(job_publication=postID).order_by('status') # Get all the applications corresponding to the offer (ordered by status : In review first)
    return render(request, 'bodies/offer_applications.html', {'applications': applications}) # Call the offer application page

def show_file(request): # The view manages the access to the applications files

    # Collect the values needed for the view
    application_number = request.GET.get('application_number','') # Get the application number
    filename_base = request.GET.get('file','') # Get the requested file's basename

    # Check the value passed in the URL
    if not filename_base or (filename_base != 'cv' and filename_base != 'coverletter'): # If the requested file's basename is not set or does not correspond to any expected value ...
        return redirect('application_management') # Redirection to the candidate's main page

    # Initialization and verification of the directory path
    dir_path = Path(settings.STATICFILES_DIRS[0]) / 'files' / application_number # Construction of the path to the application's file directory
    if not dir_path.exists(): # If the directory does not exist or is not accessible ...
        return redirect('application_management') # Redirection to the candidate's main page

    # Search the file in the directory
    matching_files = list(dir_path.glob(f"{filename_base}.*"))  # Search for the file that was asked (all extensions)
    if matching_files: # The file is found
        return FileResponse(open(matching_files[0], 'rb')) # Display the file (Read only)
    return redirect('application_management') # Redirection to the candidate's main page

def status_modification(request): # This view manages the modification of an application's status

    # Get the values needed for the views
    application_number = request.GET.get('application_number', '')  # Get the candidate's application number in the URL or set null
    new_status = request.GET.get('status', '') # Get the new status in the URL or set null
    if Application.objects.filter(application_number=application_number):
        application = Application.objects.get(application_number=application_number) # Get the application corresponding to the received application number
    else :
        previous_url = request.META.get('HTTP_REFERER', '/employee/application_management')  # Get the previous URL (offer applications)
        return redirect(previous_url)  # Return to the offer applications page

    # Check the values and update the application if they are as expected
    if (application and new_status) and new_status.isdigit() and (1 <= int(new_status) <= 3): # If the values are correct ...
        application.status = new_status # Replace the application status with the new one
        application.save() # Save the modifications in the database

        send_email("status_update_email.html",{'status': new_status, 'job_offer':application.job_publication.title},[application.candidate_mail]) # Send an email to inform the candidate of the verdict

    previous_url = request.META.get('HTTP_REFERER', '/employee/hub') # Get the previous URL (offer applications)
    if "/chat/employee" in previous_url:
        return redirect("/employee/validated_applications")
    else:
        return redirect(previous_url) # Return to the offer applications page

def employee_hub(request): # This view displays the admin menu
    if request.user.role == "admin" or request.user.role == "manager": # If the user is an admin ...
        return render(request, 'bodies/hub.html') # Call the admin menu
    return redirect('application_management') # If the user is not an admin, redirect on the employees hub

def admin_user_management(request): # This view displays the user management page
    if request.user.role == "admin": # If the user is an admin ...
        users = Employee.objects.all().order_by('employee_lastname','employee_firstname') # Get all the users ordered by names
        return render(request, 'bodies/user_management.html', {'users': users}) # Call the user management page
    return redirect('application_management') # If the user is not an admin, redirect on the employees hub
def employee_delete(request): # This view delete the employee given in the URL

    if request.user.role == "admin": # If the user is an admin ...
        userID = request.GET.get('userID','') # Get the employee id in the URL or nothing if none is given

        if userID and userID.isdigit() and Employee.objects.filter(id=int(userID)).exists(): # If the employee id is valid and exists ...
            user = get_object_or_404(Employee, id=int(userID)) # Get the employee
            if user.id != request.user.id: # The user can't delete himself
                user.delete() # Delete the employee

        return redirect('user_management') # Redirect to the user management page

    return redirect('application_management') # If the employee is not an admin, redirect to the employees page

def new_employee(request): # This view is for creating a new employee

    if request.user.role == "admin": # If the user is an admin ...

        if request.method == 'POST': # If form data is received
            form = NewEmployeeForm(request.POST) # Collect the form data

            if form.is_valid(): # Verify and clean the data
                email = form.cleaned_data['employee_email'] # Set the email of the new employee
                token = token_hex(16) # Create a token as a temporary password
                insertion = Employee(  # Prepare the insertion in the database
                    employee_firstname=form.cleaned_data['employee_firstname'],
                    employee_lastname=form.cleaned_data['employee_lastname'],
                    employee_email=email,
                    role=form.cleaned_data['role'],
                    password=make_password(token), # Set the token as a temporary password
                )
                insertion.save()  # Save the employee in the users database

                send_email("new_employee_email.html",{'token': token},[email]) # Send an email to inform the new employee that his account was created and to communicate the password

                return redirect('user_management') # Redirect to the user management page

        else : # If no data is received
            form = NewEmployeeForm() # Create an empty form
        return render(request, 'forms/new_employee_form.html', {'form': form}) # Call the new employee form

    return redirect('application_management') # If the user is not an admin, redirect to the employees page

def employee_update(request): # This view enable the edition of an employee

    if request.user.role != "admin": # If the user is not an admin ...
        return redirect('application_management') # Redirect to the employees page

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

    return render(request, 'forms/update_employee_form.html', {'form': form, 'userID': int(userID)}) # Call the update form

def admin_publication_management(request): # This view displays the publication management page
    if request.user.role == "admin" :
        posts = Publication.objects.all().order_by("archived") # Get all the publications
        return render(request, 'bodies/publication_management.html', {'posts': posts}) # Call the publication management page
    return redirect('application_management')
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
        return render(request, 'forms/publication_form.html', {'form': form, 'action': 'new'}) # Call the publication creation form

    return redirect('application_management') # If the user is not an admin, redirect to the employees page

def publication_update(request): # This view enables to update a publication

    if request.user.role != "admin": # If the user is not an admin ...
        return redirect('application_management') # Redirect to the employees page

    postID = request.GET.get('postID', '') # Get the publication id in the URL or nothing if none is passed

    if not (postID and postID.isdigit() and Publication.objects.filter(id=postID).exists): # If the employee id is not valid ...
        return redirect('publication_management') # Redirect to the publication management page
    publication = Publication.objects.get(id=int(postID))

    if request.method == 'POST': # If form data is received ...
        form = UpdatePublicationForm(request.POST, instance=publication) # Get the form data
        if form.is_valid(): # Verify and clean the form data
            form.save() # Update the publication in the database
            return redirect('publication_management') # Redirection to the publication management page

    else: # If no form data is received ...
        form = UpdatePublicationForm(instance=publication) # Get an empty update form
    return render(request, 'forms/publication_form.html', {'form': form, 'action': 'update','postID':postID}) # Call the publication update form

def delete_publication(request): # This view delete a publication

    if request.user.role == "admin": # If the user is an admin ...

        postID = request.GET.get('postID','') # Get the publication id or nothing if none is passed
        if postID and postID.isdigit() and Publication.objects.filter(id=int(postID)).exists(): # If the id is valid ...
            publication = get_object_or_404(Publication, id=int(postID)) # Get the publication
            application_emails = Application.objects.filter(job_publication=publication).values_list('candidate_mail', flat=True) # Get all the emails of the applications on this post
            email_list = list(application_emails) # Create a list with all the collected email

            send_email('publication_deletion_email.html',{'publication_name':publication.title},email_list) # Send an email to inform the candidates that the publication was deleted

            applications = Application.objects.filter(job_publication=publication) # Get all the applications of publication
            for application in applications: # Delete all the applications
                delete_candidate(application.application_number)

            publication.delete() # Delete the publication from the database

        return redirect('publication_management') # Redirection to the publication management page

    return redirect('application_management') # If the user is not an admin, redirection to the employees page

def reset_employee_password(request): # This view manages the password reset of an employee

    if request.user.role == "admin": # If the current user is an admin ...
        userID = request.GET.get('userID', '') # Get the user id in the URL or nothing if none is passed

        if userID.isdigit() and Employee.objects.filter(id=int(userID)).exists(): # If the user id is valid ...

            user = Employee.objects.get(id=int(userID)) # Get the user
            user.first_connexion = 1 # Reset the first connexion value so the user is asked to change his password at the next login
            token = token_hex(16) # Create a token as a temporary password
            user.password = make_password(token) # Set the temporary password
            user.save() # Save the password in the database

            send_email('employee_password_reset_email.html',{'token': token},[user.employee_email]) # Sends an email to communicate the reset link

            return redirect('user_management') # Redirect the user management page
    return redirect('application_management') # If the user is not an admin, redirect to the employees page


def validated_applications(request): # This view manage the page that displays all the validated applications
    if request.user.role in ["admin", "manager"]: # If the user is an admin or a manager ...
        publications = Publication.objects.filter(archived=0) # Get the publications that are not archived
        data = [] # Table to store all the data that will be displayed

        for publication in publications: # For each publication
            applications = Application.objects.filter(job_publication_id=publication.id, status=3) # Get the validated applications of the publication
            no_available_applications = not applications.exists() # If the publication has no validated applications, set the no_application boolean to true

            applications_with_unread_count = [] # Table to store the unread message count for each application
            for application in applications: # For each validated application
                try:
                    thread = Thread.objects.get(candidate=application.application_number, employee=request.user.id) # Get the thread
                    unread_count = Message.objects.filter(thread=thread, is_read=0, sender="candidate").count() # Get the unread message count
                except Thread.DoesNotExist: # If the thread doesn't exist ...
                    unread_count = 0 # The unread count is 0
                setattr(application, 'unread_count', unread_count) # Append the unread_count into the application element
                applications_with_unread_count.append(application)

            publication_data = { # Add new elements to the publication
                'title': publication.title,
                'noAvailableApplications': no_available_applications,
                'applications': applications_with_unread_count,
            }
            data.append(publication_data) # Append the publication into the displayed data

        return render(request, 'bodies/validated_applications.html', {"publications": data}) # Call the page

    return redirect('application_management') # Redirect to the application management page if the user is not allowed

def archive_publication(request): # This view archive a publication
    if request.user.role == "admin" : # If the user is an admin ...
        postId = request.GET.get('postID', '') # Get the id of the post
        if postId and postId.isdigit() and Publication.objects.filter(id=postId,archived=0).exists(): # If the post id is valid ...
            publication = Publication.objects.get(id=postId) # Get the post
            applications = Application.objects.filter(job_publication=publication) # Get the applications of the post

            for application in applications: # For each application
                clear_interviews(application.application_number,request.user.id) # Clear the interviews in the thread
                if application.status == 0 or application.status == 1: # If the application is rejected or waiting review
                    delete_candidate(application.application_number) # Delete the application
                else : # If the application was validated ...
                    application.status = 4 # Keep the application and set its status to archived
                    application.save()

            if not Application.objects.filter(job_publication=publication).exists(): # If the publication has no validated applications
                publication.delete() # Delete the publication
            else : # If the publication has validated applications
                publication.archived = 1 # Set the archive boolean to true
                publication.save()

        return redirect('publication_management') # Redirect to the publication management page
    return redirect('employee_hub') # If the user is not allowed, redirect to the employees hub

def archived_applications(request): # This view manage the archive page
    if request.user.role in ["admin", "manager"]: # If the user is an admin or a manager
        publications = Publication.objects.filter(archived=1) # Get the archived publications
        data = [] # Create an tab that will contain the displayed data

        for publication in publications: # For each publication
            applications = Application.objects.filter(job_publication_id=publication.id) # Get the applications

            publication_data = { # Merge the applications into the publication element
                'title': publication.title,
                'applications': applications,
            }
            data.append(publication_data) # Append the new element into the displayed data tab

        return render(request, 'bodies/archived_applications.html', {"publications": data}) # Call the page

    return redirect('application_management') # If the user is not allowed, redirect to the application management page

def archived_application_info(request): # This view manages the archived application detail page
    if request.user.role in ["admin","manager"] : # If the user is an admin or a manager

        candidateId = request.GET.get('candidateID', '') # Get the candidate id

        if not candidateId or not (candidateId.isdigit() and Application.objects.filter(application_number=candidateId).exists()): # If the id is not valid ...
            return redirect('/employee/logout') # Kick the user

        candidate = Application.objects.get(application_number=candidateId) # Get the candidate
        employee = Employee.objects.get(id=request.user.id) # Get the employee

        if Thread.objects.filter(candidate_id=candidate.application_number, employee_id=employee.id).exists(): # If the thread exists

            thread = Thread.objects.get(candidate_id=candidate.application_number, employee_id=employee.id) # Get the thread
            encryption_key = get_encryption_key(thread) # Get the encryption key of the thread

            messages = Message.objects.filter(thread=thread).order_by('timestamp') # Get the messages of the thread

            for item in messages: # For each message
                try: # Try to decrypt the message
                    item.content = decrypt_message(item.content, encryption_key) # Message decryption
                except Exception: # If the message can't be decrypted
                    item.content = "[Message corrompu ou clé incorrecte]" # Display an decryption error in the message

        else : # If there are no messages ...
            messages = [] # Create an empty tab to avoid errors because the value is unexisting

        return render(request, 'bodies/archived_application_info.html',{'messages': messages, 'application': candidate}) # Call the page
    return redirect('/employee/hub') # If the user is not allowed, redirect to the employees' main page

def application_delete(request): # This view manage the deletion of an application
    if request.user.role == "admin": # If the user is an admin
        candidateId = request.GET.get('candidateID', '') # Get the candidate id
        if candidateId and candidateId.isdigit() and Application.objects.filter(application_number=candidateId).exists(): # If the id is valid ...
            if  Application.objects.get(application_number=candidateId).status == 4: # If the application is archived ...
                delete_candidate(candidateId) # Delete the application
        return redirect('/employee/archived_applications') # Redirect to the archived application page
    return redirect("/employee/hub") # If the user is not allowed, redirect to the employees' hub


