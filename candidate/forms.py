import os # Import OS management module
from django import forms # Import Django form module
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator  # Import Django Validators
from candidate.models import Application # Import the application model
##################################################################################################################

# Form used for the login system
class ApplicationLoginForm(forms.Form):
    application_number = forms.CharField(max_length=11,widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrez votre numéro de candidature'}),label="Numéro de candidature",validators=[RegexValidator(regex='^\d{11}$',message="Format du numéro de candidature incorrect")]) # Input Application Number
    password = forms.CharField(max_length=200,widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Entrez votre mot de passe'}), label="Mot de passe") # Input Password

# Form used to update some data about an existing application
class ApplicationUpdateForm(forms.ModelForm):
    class Meta:
        model = Application # Define the model linked to the form
        fields = ['candidate_firstname', 'candidate_lastname', 'candidate_mail', 'candidate_phone']  # Editable Fields

    candidate_firstname = forms.CharField(max_length=50,widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'Entrez votre prénom'})) # Input candidate's firstname
    candidate_lastname = forms.CharField(max_length=50,widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'Entrez votre prénom'})) # Input candidate's lastname
    candidate_mail = forms.EmailField(max_length=100,widget=forms.EmailInput(attrs={'class': 'form-control','placeholder': 'Entrez votre emails'})) # Input candidate's mail
    candidate_phone = forms.CharField(required=False,min_length=10,max_length=10, widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'Entrez votre numéro de téléphone'}),validators=[RegexValidator(regex="^0[1-9](\d{2}){4}$",message="Le numéro de téléphone doit contenir exactement 10 chiffres.")]) # Input candidate's phone number
    cv = forms.FileField(required=False,widget=forms.FileInput(attrs={'class': 'form-control-file', 'accept': 'image/*,.pdf'}))  # Input candidate's CV file
    cover_letter = forms.FileField(required=False,widget=forms.FileInput(attrs={'class': 'form-control-file', 'accept': '.pdf,.txt,.doc,.docx'}))  # Input candidate's cover letter file

    def clean(self): # function for personalized form data verification
        cleaned_data = super().clean() # Default input cleaning and validation function

        firstname = cleaned_data.get('candidate_firstname') # Get the candidate firstname cleaned by the default function
        lastname = cleaned_data.get('candidate_lastname') # Get the candidate lastname cleaned by the default function

        if firstname: # If a firstname value is defined
            cleaned_data['candidate_firstname'] = firstname.capitalize() # Reformat the value : first letter is set in uppercase and the rest is set in lowercase
        if lastname:
            cleaned_data['candidate_lastname'] = lastname.upper() # # Reformat the value : all the text is set in uppercase

        # Uploaded Files Retrieving
        cv = cleaned_data.get('cv')  # # Get the cv cleaned by the default function
        cover_letter = cleaned_data.get('cover_letter')  # Get the cover letter cleaned by the default function

        # CV File Extension Verification
        if cv : # If cv file value is set ...
            cv_allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg','.pdf']  # List of allowed extensions for the CV file
            if os.path.splitext(cv.name)[1].lower() not in cv_allowed_extensions:  # Check if the uploaded file's extension is in the list
                raise ValidationError(f"L'extension n'est pas autorisée. Uniquement les fichiers PDF ou images sont acceptés")  # Send error if the extension is not in the list

            # File Size Verification
            if not cv or (cv.size == None or cv.size > 30000000):  # If the CV or Cover letter file is bigger than 30Mo ...
                raise forms.ValidationError("Le fichier ne doit pas être vide et être inférieur à 30Mo")  # Sends the error

        # Cover Letter Extension Verification
        if cover_letter : # If cover letter file is set ...
            cover_letter_allowed_extensions = ['.pdf', '.txt', '.doc','.docx']  # List of allowed extensions for the cover letter file
            if os.path.splitext(cover_letter.name)[1].lower() not in cover_letter_allowed_extensions:  # Check if the uploaded file's extension is in the list
                raise ValidationError(f"L'extension n'est pas autorisée. Uniquement les fichiers texte et PDF sont acceptés")  # Send error if the extension is not in the list

            # File Size Verification
            if not cover_letter or (cover_letter.size == None or cover_letter.size > 30000000):  # If the CV or Cover letter file is bigger than 30Mo ...
                raise forms.ValidationError("Le fichier ne doit pas être vide et être inférieur à 30Mo")  # Sends the error

        return cleaned_data

# Form used to collect the user email
class CandidateEmailForm(forms.Form):
    email = forms.EmailField(max_length=100,widget=forms.EmailInput(attrs={'class': 'form-control','placeholder': 'Entrez votre email'})) # Input User Email

# Form used to collect the user Application Number
class ApplicationNumberForm(forms.Form):
    application_number = forms.CharField(max_length=11,widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrez votre numéro de candidature'}),validators=[RegexValidator(regex='^\d{11}$',message="Numéro de candidature incorrect")]) # Input Application Number

# Form used by the candidate to change his password
class CandidateChangePasswordForm(forms.Form):

    password = forms.CharField(max_length=200,widget=forms.PasswordInput(attrs={'id':'password','class': 'form-control', 'placeholder': "Entrez votre nouveau mot de passe"}),validators=[RegexValidator(regex='^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[\W_]).{8,}$',message='Le mot de passe doit contenir au moins 8 caractères dont une majuscule, une minuscule, un chiffre et un caractère spécial')]) # Password input
    confirm_password = forms.CharField(max_length=200,widget=forms.PasswordInput(attrs={'id':'confirm','class': 'form-control', 'placeholder': "Confirmez votre nouveau mot de passe"})) # Password Confirmation Input

    def clean(self):
        cleaned_data = super().clean() # Get the form data cleaned by the default cleaning function
        password = cleaned_data.get('password') # Get the input password
        confirm_password = cleaned_data.get('confirm_password') # Get the input password confirmation

        if password != confirm_password: # If the password doesn't match the confirmation ...
            raise ValidationError("Les mots de passe ne correspondent pas") # Send an error : the two fields must match
