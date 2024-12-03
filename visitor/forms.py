from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email, RegexValidator

class ApplicationForm(forms.Form):
    name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrez votre nom'})) # Input candidate's name
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Entrez votre mail'})) # Input candidate's mail
    firstname = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrez votre prénom'})) # Input candidate's firstname
    phone = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrez votre numéro de téléphone'})) # Input candidate's phone number
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Entrez un mot de passe', 'id': 'password'})) # Input candidate's password
    confirm = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmez le mot de passe', 'id': 'confirm'})) # Input candidate's password confirmation
    cv = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control-file', 'accept': 'image/*,.pdf'})) # Input candidate's CV file
    cover_letter = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control-file','accept':'.pdf,.txt,.doc,.docx'})) # Input candidate's cover letter file

    def clean(self): #verify form data
        cleaned_data = super().clean() # Default input cleaning and validation function
        email = cleaned_data.get('email') # Get the email cleaned by the default function
        try:
            validate_email(email) # Check if the input mail is the right format
        except ValidationError as e: # If an error occur ...
            raise forms.ValidationError(e.message_dict) #Sends the error

        password = cleaned_data.get('password') # Get the password cleaned by the default function
        confirm = cleaned_data.get('confirm') # Get the confirmed password cleaned by the default function

        if password != confirm: # If the password and confirm password input are not the same ...
            raise forms.ValidationError("Les mots de passe ne correspondent pas.") # Sends the error
        if not RegexValidator(regex='^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[\W_]).{8,}$',message=password): # If the password doesn't match the conditions ...
            raise forms.ValidationError("Le mot de passe doit contenir au moins 8 caractères dont une majuscule, une minuscule, un chiffre et un caractère spécial") # Sends the error

        phone = cleaned_data.get('phone') # Get the phone number cleaned by the default function
        if RegexValidator(regex="/^\d{10}$/;",message=phone): # If the input size is anything else than a 10 number string ...
            raise forms.ValidationError("Le numéro de téléphone doit contenir exactement 10 chiffres.") # Sends the error

        cv=cleaned_data.get('cv') # # Get the cv cleaned by the default function
        cover_letter = cleaned_data.get('cover_letter') # Get the cover letter cleaned by the default function
        if (cv.size == None or cv.size > 30000000) or (cover_letter.size == None or cover_letter.size > 30000000) : # If the CV or Cover letter file is bigger than 30Mo ...
            raise forms.ValidationError("Le fichier ne doit pas être vide et être inférieur à 30Mo") # Sends the error

        return cleaned_data