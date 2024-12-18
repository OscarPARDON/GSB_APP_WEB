from django import forms
from django.core.validators import RegexValidator, EmailValidator


class ApplicationForm(forms.Form):

    name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrez votre nom'})) # Input candidate's name
    email = forms.EmailField(max_length=100,widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Entrez votre mail'}),validators=[EmailValidator(message="Email incorrect")]) # Input candidate's mail
    firstname = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrez votre prénom'})) # Input candidate's firstname
    phone = forms.CharField(required=False,min_length=10,max_length=10, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrez votre numéro de téléphone'}),validators=[RegexValidator(regex="^0[1-9](\d{2}){4}$",message="Le numéro de téléphone doit contenir exactement 10 chiffres.")]) # Input candidate's phone number
    password = forms.CharField(max_length=200,widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Entrez un mot de passe', 'id': 'password'}),validators=[RegexValidator(regex='^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[\W_]).{8,}$',message='Le mot de passe doit contenir au moins 8 caractères dont une majuscule, une minuscule, un chiffre et un caractère spécial')]) # Input candidate's phone number
    confirm = forms.CharField(max_length=200,widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmez le mot de passe', 'id': 'confirm'})) # Input candidate's password confirmation
    cv = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control-file', 'accept': 'image/*,.pdf'})) # Input candidate's CV file
    cover_letter = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control-file','accept':'.pdf,.txt,.doc,.docx'})) # Input candidate's cover letter file

    def clean(self): #verify form data
        cleaned_data = super().clean() # Default input cleaning and validation function

        password = cleaned_data.get('password') # Get the password cleaned by the default function
        confirm = cleaned_data.get('confirm') # Get the confirmed password cleaned by the default function
        if password != confirm: # If the password and confirm password input are not the same ...
            raise forms.ValidationError("Les mots de passe ne correspondent pas.") # Sends the error

        cv=cleaned_data.get('cv') # # Get the cv cleaned by the default function
        cover_letter = cleaned_data.get('cover_letter') # Get the cover letter cleaned by the default function
        if (cv.size == None or cv.size > 30000000) or (cover_letter.size == None or cover_letter.size > 30000000) : # If the CV or Cover letter file is bigger than 30Mo ...
            raise forms.ValidationError("Le fichier ne doit pas être vide et être inférieur à 30Mo") # Sends the error

        return cleaned_data