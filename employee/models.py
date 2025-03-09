from django.db import models # Import Django Model Module
############################################################################################################

# Employee Model
class Employee(models.Model):
    employee_lastname = models.CharField(max_length=50) # Employee's lastname
    employee_firstname = models.CharField(max_length=50) # Employee's firstname
    employee_email = models.EmailField(max_length=200,unique=True) # Employee's emails also used as login id (unique)
    password = models.CharField(max_length=200) # Employee's password (hashed)
    role = models.CharField(max_length=100,default='employee') # Role of the employee (Admin or Employee)
    last_login = models.DateTimeField(auto_now=True) # Last time the employee logged in
    first_connexion = models.BooleanField(default=True) # Value to know if the user should change password

    def check_password(self, raw_password): # Function to compare the input password with the password in the database
        from django.contrib.auth.hashers import check_password # Import Django Module to check the password
        return check_password(raw_password, self.password) # Compare the password and return if the passwords are the same or not

    @property
    def is_authenticated(self): # Property of the employee witch determine if the user is logged in or not
        return True

    @property
    def is_active(self): # Property of the employee witch determine if the user active in or not
        return True