import os # Import Python Operating System Management Module
from pathlib import Path # Import File Path Management Module
from secrets import token_hex
from django.conf import settings # Import Settings Variables
from django.contrib.auth import authenticate, login, logout # Import Django Authentication Module
from django.contrib.auth.hashers import make_password
from django.core.mail import EmailMessage
from django.http import Http404, FileResponse # Import Django HTTP Module
from django.shortcuts import render, redirect, get_object_or_404 # Shortcut to import some Django Modules
from django.template.loader import render_to_string
from .forms import ApplicationLoginForm, ApplicationUpdateForm, \
    CandidateEmailForm, ApplicationNumberForm, CandidateChangePasswordForm  # Import the Login and Update Forms
from .models import Application # Import the Application Model
######################################################################################################################

def candidate_login(request): # This views manages the candidates login process

    if request.method == 'POST': # If form data is received ...
        form = ApplicationLoginForm(request.POST)  # Collect the form data

        if form.is_valid(): # Proceed the form data validation, if no problem is detected ...

            # Collect the input values (cleaned)
            application_number = form.cleaned_data['application_number'] # Collect the cleaned application number
            password = form.cleaned_data['password'] # Collect the cleaned password

            # Authentication
            user = authenticate(request, application_number=application_number, password=password)
            if user: # If the authentication was successful ...
                login(request, user)  # Log the user in
                return redirect('candidate_hub') # Redirect to the candidate's main page
            else: # If the authentication failed ...
                form.add_error(None, "Numéro de candidature ou mot de passe incorrect.") # Send back to the login page with a message

    else: # If no form data is received

        #Application Number autocompletion if the user access the login via the success application submition page
        application_number = request.GET.get('application_number', '') # Try to collect the application number in the URL
        if application_number: # If an application number is passed in the URL
            form = ApplicationLoginForm(initial={'application_number': application_number}) # Autocomplete Application Number in the login form
        else : # If no application number is passed in the URL
            form = ApplicationLoginForm() # Set New login form

    return render(request, 'forms/candidate_login.html', {'form': form}) # Call the login page


def candidate_logout(request): # View to log out the user
    logout(request) # Log out the user
    response = redirect('/') # Set the redirection url to the candidate homepage
    response.delete_cookie('sessionid') # Delete the session cookie
    return response # Redirect to the candidate homepage

def candidate_hub(request): # This view manages the candidate's main page

    # Get the data needed for the view
    application = request.user # Get the candidate's data

    # Checking the availability of the candidate's files
    dir_path = Path(settings.STATICFILES_DIRS[0]) / 'files' / application.application_number # Path to the candidate's files directory
    filename_bases = ["CV", "coverletter"] # List of the searched files basename
    file_data = {} # Initialization of the dictionary that will store the test results
    for filename_base in filename_bases: # For all the files basename in the list
        matching_files = list(dir_path.glob(f"{filename_base}.*")) # Search for a file corresponding to the basename in the candidate's directory
        if matching_files: # A file is found ...
            file_data[filename_base] = 1 # Set the test value to 1 : the file exists and is accessible
        else: # No file is found ...
            file_data[filename_base] = 0  # Set the test value to 1 : the file doesn't exist, or it is inaccessible

    return render(request, 'bodies/candidate_hub.html', {'application':application, 'file_data':file_data}) # Call the candidate's main page

def show_file(request): # The view manages the access to the candidate's files

    # Collect the values needed for the view
    application_number = request.user.application_number # Get the candidate's application number
    filename_base = request.GET.get('file','') # Get the requested file's basename

    # Check the value passed in the URL
    if not filename_base or (filename_base != 'cv' and filename_base != 'coverletter'): # If the requested file's basename is not set or does not correspond to any expected value ...
        return redirect('candidate_hub') # Redirection to the candidate's main page

    # Initialization and verification of the candidate's file directory path
    dir_path = Path(settings.STATICFILES_DIRS[0]) / 'files' / application_number # Construction of the path to the candidate's file directory
    if not dir_path.exists(): # If the directory does not exist or is not accessible ...
        raise Http404("Répertoire introuvable.") # Send error 404

    # Search the file in the directory
    matching_files = list(dir_path.glob(f"{filename_base}.*"))  # Search for the file that was asked (all extensions)
    if matching_files: # The file is found
        return FileResponse(open(matching_files[0], 'rb')) # Display the file (Read only)
    raise Http404("Fichier introuvable.") # The file is not found, send error 404

def candidate_delete(request): # This views manages the application deletion
    application_number = request.user.application_number # Get the candidate's application number

    # Delete the candidate's files and delete the candidate's directory
    dir_path = Path(settings.STATICFILES_DIRS[0]) / 'files' / application_number # Construction of the path to the candidate's directory
    if dir_path.exists(): # If the directory exist ...
        files_to_remove = ["cv.*", "coverletter.*"] # List of the files to remove
        for pattern in files_to_remove: # For all the files in the list ...
            matching_files = list(dir_path.glob(pattern))  # Searching for the file corresponding to the file in the list
            if matching_files: # If the file is found ...
                os.remove(matching_files[0]) # Delete the file
        os.rmdir(dir_path) # Delete the candidate's directory

    # Delete the application from the database
    application = get_object_or_404(Application, application_number=application_number) # Get the application or send 404 error if it's not found in the databse

    html_content = render_to_string('emails/deletion_confirmation_email.html',{'job_offer':application.job_publication.title}) # Get the Email Template
    email = EmailMessage("GSB Recrutement", html_content, settings.EMAIL_HOST_USER, [application.candidate_mail]) # Configure the Email
    email.content_subtype = 'html' # Set the email content type to HTML
    email.send(fail_silently=True) # Send the Email

    logout(request) # Log the user out before deletion
    application.delete() # Delete the application from the database
    return redirect('/')  # Redirection to the visitor page

def candidate_update(request): # This view manage the modification of an application
    application = get_object_or_404(Application, application_number=request.user.application_number) # Get the candidate's application from the database

    if request.method == 'POST': # If form data is received
        form = ApplicationUpdateForm(request.POST, request.FILES, instance=application) # Collect the form data

        if form.is_valid(): # Cleaning and verification of the form data
            form.save() # Update the application in the database

            # Manage the files
            files_dir = Path(settings.STATICFILES_DIRS[0]) / 'files' / application.application_number # Construction of the path to the candidate's file directory
            files_dir.mkdir(parents=True, exist_ok=True)  # If the candidate doesn't have a file repository, one is created

            if 'cv' in request.FILES: # If a new CV file is received ...
                cv_file = request.FILES['cv'] # Collect the input file
                with open(files_dir / f"CV{Path(cv_file.name).suffix}", 'wb+') as destination: # Save the file in the directory
                    for chunk in cv_file.chunks():
                        destination.write(chunk)

            if 'cover_letter' in request.FILES: # If a new cover lletter file is received ...
                coverletter_file = request.FILES['cover_letter'] # get the input file
                with open(files_dir / f"coverletter{Path(coverletter_file.name).suffix}", 'wb+') as destination: # Save the file in the directory
                    for chunk in coverletter_file.chunks():
                        destination.write(chunk)

            return redirect('/candidate/hub')  # Redirection to the candidate's main page

    else: # No form data is received
        form = ApplicationUpdateForm(instance=application) # Get the prefilled application update form

    return render(request, 'forms/update_application_form.html', {'form': form}) # Call the update form page

def forgot_application_number(request): # This function manage the forgot application number form
    if request.method == "POST": # If form data is received
        form = CandidateEmailForm(request.POST) # Get the form data
        if form.is_valid(): # If the data is valid ...
            if Application.objects.filter(candidate_mail=form.cleaned_data['email']).exists(): # If the email is linked to any application ...
                application = Application.objects.filter(candidate_mail=form.cleaned_data['email']) # Get the application corresponding to the email

                has_multiple_applications = 0
                if len(application) > 1 :
                    has_multiple_applications = 1
                html_content = render_to_string('emails/forgot_application_number_email.html',{'application': application,'has_multiple_applications':has_multiple_applications}) # Get the email template
                email = EmailMessage("GSB Recrutement", html_content, settings.EMAIL_HOST_USER, [form.cleaned_data['email']]) # Configure the email
                email.content_subtype = 'html' # Set the email content type to html
                email.send(fail_silently=True) # Send the email

            return render(request,'bodies/sent_confirmation.html',{'content':'numéro de candidature','email':form.cleaned_data['email']}) # Call the email confirmation page
    else: # If no form data is received ...
        form = CandidateEmailForm() # Create an empty form
    return render(request, 'forms/candidate_email_form.html', {'form':form}) # Call the email form

def forgot_password(request): # This function manages the forgot password form
    if request.method == "POST": # If form data is received ...
        form = ApplicationNumberForm(request.POST) # Get the form data
        if form.is_valid(): # If the form data is valid ...
            if Application.objects.filter(application_number=form.cleaned_data['application_number']).exists(): # If the application number exists
                application = Application.objects.get(application_number=form.cleaned_data['application_number']) # Get the application
                password_reset_token = token_hex(32) # Create a password reset token for the application
                application.password_reset_token = password_reset_token # Set the reset token password
                application.save() # Save the reset token password token in the database

                html_content = render_to_string('emails/reset_password_email.html',{'password_reset_token': password_reset_token,'application_number': form.cleaned_data['application_number'],'job_offer':application.job_publication.title}) # Get the email template
                email = EmailMessage("GSB Recrutement", html_content, settings.EMAIL_HOST_USER,[application.candidate_mail]) # Configure the email
                email.content_subtype = 'html' # Set the email content type to html
                email.send(fail_silently=True) # Send the email
            return render(request,'bodies/sent_confirmation.html',{'content':'lien de réinitialisation du mot de passe'}) # Call the email confirmation page
    else: # If no from data is received ...
        form = ApplicationNumberForm() # Create an empty form
    return render(request,'forms/candidate_application_number_form.html',{'form':form}) # Call the application number form

def reset_password(request): # This function manage the candidate password reset
    application_number = request.GET.get('application_number','') # Get the application number in the URL or nothing if none is passed
    token = request.GET.get('token','') # Get the reset token in the URL or nothing if none is passed
    if Application.objects.filter(application_number=application_number).exists() and Application.objects.get(application_number=application_number).password_reset_token is not None: # If the application number exists and a reset token was created for this application ...
        application = Application.objects.get(application_number=application_number) # Get the application
        if application.password_reset_token == token: # If the token match the token in the database ...
            if request.method == "POST": # If form data is received ...
                form = CandidateChangePasswordForm(request.POST) # Get the form data
                if form.is_valid(): # If the form data is received ...
                    application.password_reset_token = None # Delete the password reset token as it is used
                    application.candidate_password = make_password(form.cleaned_data['password']) # Set the new password
                    application.save() # Save new password in the database

                    html_content = render_to_string('emails/confirm_password_change_email.html',{'job_offer':application.job_publication.title}) # Get the email template
                    email = EmailMessage("GSB Recrutement", html_content, settings.EMAIL_HOST_USER,[application.candidate_mail]) # Configure the email
                    email.content_subtype = 'html' # Set the email content type to html
                    email.send(fail_silently=True) # Send the email
                    return redirect('/candidate/login') # Redirect to the user page
            else: # If no form data is received
                form = CandidateChangePasswordForm() # Create an empty form
            return render(request,'forms/candidate_change_password_form.html',{'form':form,'application_number':application.application_number,'token':application.password_reset_token}) # Call the password change form
    return redirect('/candidate/login') # If the application number or the token is not valid, redirect to the login page
