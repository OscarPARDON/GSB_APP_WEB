from django import forms # Import Django form module
from django.core.validators import EmailValidator  # Import Django Email Validator
from candidate.models import Application # Import the Application Model
########################################################################################################"

# Form used to by the employee login system
class EmployeeLoginForm(forms.Form):
    employee_id = forms.EmailField(max_length=200,widget=forms.EmailInput(attrs={'class': 'form-control','placeholder':'Entrez votre identifiant'}),validators=[EmailValidator(message="Identifiant incorrect")]) # Employee Identifer (Mail)
    password = forms.CharField(max_length=200,widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder':'Entrez votre mot de passe'})) # Employee password

# Form used to update the status of an application
class ApplicationStatusForm(forms.ModelForm):

    class Meta:
        model = Application # Model linked to the form
        fields = ['status'] # Updated field

    application_number = forms.CharField(widget=forms.TextInput(),max_length=11) # Application Number
    new_status = forms.IntegerField(widget=forms.TextInput(attrs={'hidden':'true'})) # New status