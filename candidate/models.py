from django.db import models # Import Django Model Module
from django.contrib.auth.models import AbstractBaseUser # Import Django Authentication Module
from visitor.models import Publication #Import the Publication Model
##############################################################################################################

class Application(models.Model): # Application Model
    application_number = models.CharField(max_length=11, unique=True) # Unique Number of the application (Format : YYYYMMDDNNN)
    candidate_firstname = models.CharField(max_length=50) # Firstname of the candidate
    candidate_lastname = models.CharField(max_length=50) # Lastname of the candidate
    candidate_mail = models.CharField(max_length=100) # Mail of the candidate
    candidate_phone = models.CharField(default=None,max_length=10,blank=True, null=True)  # Phone Number of the candidate (Optional)
    candidate_password = models.CharField(max_length=200) # Password to access to the application data
    status = models.IntegerField(default=1) # Status of the application (In review, Rejected, Accepted)
    job_publication = models.ForeignKey(Publication,on_delete=models.CASCADE,related_name='publication') # Job offer that the candidate applied for
    creation_date = models.DateTimeField(auto_now_add=True) # Date of creation of the application
    last_login = models.DateTimeField(auto_now=True) # Last time the candidate logged in

    def check_password(self, raw_password): # Function to compare the input password with the password in the databasr
        from django.contrib.auth.hashers import check_password # Import Django Module to check the password
        return check_password(raw_password, self.candidate_password) # Compare the password and return if the passwords are the same or not

    @property
    def is_authenticated(self): # Property of the application witch determine if the user is logged in or not
        return True

    @property
    def is_active(self): # Property of the application witch determine if the user active in or not
        return True


