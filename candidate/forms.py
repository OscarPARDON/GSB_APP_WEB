from django import forms # Import Django form module
from django.core.validators import RegexValidator, EmailValidator  # Import Django Validators
from candidate.models import Application # Import the application model
##################################################################################################################

# Form used for the login system
class ApplicationLoginForm(forms.Form):
    application_number = forms.CharField(max_length=11,widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrez votre numéro de candidature'}),label="Numéro de candidature",validators=[RegexValidator(regex='^\d{11}$',message="Format du numéro de candidature incorrect")]) # Input Application Number
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Entrez votre mot de passe'}), label="Mot de passe") # Input Password

# Form used to update some data about an existing application
class ApplicationUpdateForm(forms.ModelForm):
    class Meta:
        model = Application # Define the model linked to the form
        fields = ['candidate_firstname', 'candidate_lastname', 'candidate_mail', 'candidate_phone']  # Editable Fields

    candidate_firstname = forms.CharField(max_length=50,widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'Entrez votre prénom'})) # Input candidate's firstname
    candidate_lastname = forms.CharField(max_length=50,widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'Entrez votre prénom'})) # Input candidate's lastname
    candidate_mail = forms.EmailField(max_length=100,widget=forms.EmailInput(attrs={'class': 'form-control','placeholder': 'Entrez votre email'}),validators=[EmailValidator(message="Email incorrect")]) # Input candidate's mail
    candidate_phone = forms.CharField(required=False,min_length=10,max_length=10, widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'Entrez votre numéro de téléphone'}),validators=[RegexValidator(regex="^0[1-9](\d{2}){4}$",message="Le numéro de téléphone doit contenir exactement 10 chiffres.")]) # Input candidate's phone number
    cv = forms.FileField(required=False,widget=forms.FileInput(attrs={'class': 'form-control-file', 'accept': 'image/*,.pdf'}))  # Input candidate's CV file
    cover_letter = forms.FileField(required=False,widget=forms.FileInput(attrs={'class': 'form-control-file', 'accept': '.pdf,.txt,.doc,.docx'}))  # Input candidate's cover letter file

    def clean(self): # function for personalized form data verification
        cleaned_data = super().clean() # Default input cleaning and validation function

        if cleaned_data.get('cv') : # If cv field is not empty
            cv=cleaned_data.get('cv') # # Get the cv cleaned by the default function
            if cv.size == None or cv.size > 30000000 : # If the size of the file is none or above 30Mo ...
                raise forms.ValidationError("Le fichier ne doit pas être vide et doit être inférieur à 30Mo")  # Sends the error

        if cleaned_data.get('cover_letter') : # If cover letter field is not empty
            cover_letter = cleaned_data.get('cover_letter') # Get the Cover Letter cleaned by the default function
            if cover_letter.size == None or cover_letter.size > 30000000 : # If the Cover letter file is None or bigger than 30Mo ...
                raise forms.ValidationError("Le fichier ne doit pas être vide et être inférieur à 30Mo") # Sends the error

        return cleaned_data # Return the cleaned data if no error is detected