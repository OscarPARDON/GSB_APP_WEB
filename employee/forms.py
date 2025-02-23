from django import forms # Import Django form module
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, RegexValidator  # Import Django Email Validator
from candidate.models import Application # Import the Application Model
from employee.models import Employee
from visitor.models import Publication
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

# Form used to create a new employee
class NewEmployeeForm(forms.Form):

    employee_lastname = forms.CharField(max_length=50,widget=(forms.TextInput(attrs={'class': 'form-control', 'placeholder':"Entrez le nom de famille de l'employé"}))) # Lastname of the employee
    employee_firstname = forms.CharField(max_length=50, widget=(forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Entrez le prénom de l'employé"}))) # Firstname of the employee
    employee_email = forms.EmailField(max_length=200, widget=(forms.EmailInput(attrs={'class': 'form-control', 'placeholder': "Entrez l'emails professionel de l'employé"}))) # Email of the employee
    role = forms.ChoiceField(choices=[('employee','Employé'),('admin','Admin'),('manager','Manager')],widget=forms.Select(attrs={'class': 'form-control'})) # Role of the employee (Admin or Employee)

    def clean(self):
        cleaned_data = super().clean() # Get the form data cleaned by the default clean function

        email = cleaned_data.get('employee_email')

        if Employee.objects.filter(employee_email=email).exists():
            raise ValidationError("Un autre utilisateur utilise déja cet email.")

        firstname = cleaned_data.get('employee_firstname')  # Get the employee firstname cleaned by the default function
        lastname = cleaned_data.get('employee_lastname')  # Get the employee lastname cleaned by the default function

        if firstname:  # If a firstname value is defined
            cleaned_data['employee_firstname'] = firstname.capitalize()  # Reformat the value : first letter is set in uppercase and the rest is set in lowercase
        if lastname: # If a lastname value is defined
            cleaned_data['employee_lastname'] = lastname.upper()  # Reformat the value : all the text is set in uppercase

        return cleaned_data # Return the cleaned values

# Form used to update employees
class UpdateEmployeeForm(forms.ModelForm):

    class Meta:
        model = Employee # Model linked to the form
        fields = ['employee_lastname','employee_firstname','employee_email','role'] # Fields to modify

    employee_lastname = forms.CharField(max_length=50, widget=(forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Entrez le nom de famille de l'employé"}))) # Lastname of the employee
    employee_firstname = forms.CharField(max_length=50, widget=(forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Entrez le prénom de l'employé"}))) # FIrstname of the employee
    employee_email = forms.EmailField(max_length=200, widget=(forms.EmailInput(attrs={'class': 'form-control', 'placeholder': "Entrez l'emails professionel de l'employé"}))) # Email of the employee
    role = forms.ChoiceField(choices=[('employee', 'Employé'), ('admin', 'Admin'),('manager','Manager')],widget=forms.Select(attrs={'class': 'form-control'})) # Role of the employee

    def clean(self):
        cleaned_data = super().clean() # Get the form data cleaned by the default function

        firstname = cleaned_data.get('employee_firstname')  # Get the employee firstname cleaned by the default function
        lastname = cleaned_data.get('employee_lastname')  # Get the employee lastname cleaned by the default function

        if firstname:  # If a firstname value is defined
            cleaned_data['employee_firstname'] = firstname.capitalize()  # Reformat the value : first letter is set in uppercase and the rest is set in lowercase
        if lastname: # If a lastname value is defined
            cleaned_data['employee_lastname'] = lastname.upper()  # Reformat the value : all the text is set in uppercase

        if (self.instance.employee_firstname != cleaned_data['employee_firstname'] or self.instance.employee_lastname != cleaned_data['employee_lastname']) and Employee.objects.filter(employee_firstname= cleaned_data['employee_firstname'],employee_lastname= cleaned_data['employee_lastname']).exists():
            raise ValidationError("Cet employé existe déjà")  # Sends an error : an employee with this name already exists
        if self.instance.employee_email !=  cleaned_data['employee_email'] and Employee.objects.filter(employee_email= cleaned_data['employee_email']).exists():
            raise ValidationError("Cet emails est déjà utilisé par un employé, veuillez en renseigner un autre")  # Sends an error : the emails is already used

        return cleaned_data # Return the cleaned values

# Form used when the employee wants to edit himself (Role is disabled)
class UpdateSelfForm(forms.ModelForm):

    class Meta:
        model = Employee # Model linked to the form
        fields = ['employee_lastname','employee_firstname','employee_email'] # Fields to modify

    employee_lastname = forms.CharField(max_length=50, widget=(forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Entrez le nom de famille de l'employé"}))) # Lastname of the employee
    employee_firstname = forms.CharField(max_length=50, widget=(forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Entrez le prénom de l'employé"}))) # Firstname of the employee
    employee_email = forms.EmailField(max_length=200, widget=(forms.EmailInput(attrs={'class': 'form-control', 'placeholder': "Entrez l'emails professionel de l'employé"}))) # Email of the employee

    def clean(self):
        cleaned_data = super().clean() # Get the form data cleaned by the default function

        firstname = cleaned_data.get('employee_firstname')  # Get the user firstname cleaned by the default function
        lastname = cleaned_data.get('employee_lastname')  # Get the user lastname cleaned by the default function

        if firstname:  # If a firstname value is defined
            cleaned_data['employee_firstname'] = firstname.capitalize()  # Reformat the value : first letter is set in uppercase and the rest is set in lowercase
        if lastname:
            cleaned_data['employee_lastname'] = lastname.upper()  # Reformat the value : all the text is set in uppercase

        if (self.instance.employee_firstname != cleaned_data['employee_firstname'] or self.instance.employee_lastname != cleaned_data['employee_lastname']) and Employee.objects.filter(employee_firstname= cleaned_data['employee_firstname'],employee_lastname= cleaned_data['employee_lastname']).exists():
            raise ValidationError("Cet employé existe déjà")  # Sends an error : an employee with this name already exists
        if self.instance.employee_email !=  cleaned_data['employee_email'] and Employee.objects.filter(employee_email= cleaned_data['employee_email']).exists():
            raise ValidationError("Cet emails est déjà utilisé par un employé, veuillez en renseigner un autre")  # Sends an error : the emails is already used


        return cleaned_data # Return the cleaned values

# Form used to create a new publication
class NewPublicationForm(forms.Form):

    title = forms.CharField(max_length=100, widget=(forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Entrez le titre de la nouvelle publication"}))) # Title of the publication
    description = forms.CharField(max_length=500,widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': "Entrez le description de la nouvelle publication",'style':'resize:none'})) # Description of the publication

# Form used to update a publication
class UpdatePublicationForm(forms.ModelForm):

    class Meta:
        model = Publication # Model linked to the form
        fields = ['title','description'] # Fields to update

    title = forms.CharField(max_length=100, widget=(forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Entrez le titre de la nouvelle publication"}))) # Title of the publication
    description = forms.CharField(max_length=500,widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': "Entrez le description de la nouvelle publication",'style':'resize:none'})) # Description of the publication

# Form used to change the password of an employee
class EmployeeChangePasswordForm(forms.ModelForm):

    class Meta:
        model = Employee # Model linked to the form
        fields = ['password'] # Fields updated

    password = forms.CharField(max_length=200,widget=forms.PasswordInput(attrs={'id':'password','class': 'form-control', 'placeholder': "Entrez votre nouveau mot de passe"}),validators=[RegexValidator(regex='^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[\W_]).{8,}$',message='Le mot de passe doit contenir au moins 8 caractères dont une majuscule, une minuscule, un chiffre et un caractère spécial')]) # New password Input
    confirm_password = forms.CharField(max_length=200,widget=forms.PasswordInput(attrs={'id':'confirm','class': 'form-control', 'placeholder': "Confirmez votre nouveau mot de passe"})) # Confirm new password input

    def clean(self):
        cleaned_data = super().clean() # Get the form data cleaned by the default function
        password = cleaned_data.get('password') # Get the input password
        confirm_password = cleaned_data.get('confirm_password') # Get the input password confirmation

        if password != confirm_password: # If the passwords don't match ...
            raise ValidationError("Les mots de passe ne correspondent pas") # Send an error, the fields must match
