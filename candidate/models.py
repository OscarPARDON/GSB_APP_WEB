from django.db import models



class Application(models.Model): #Application Model
    application_number = models.CharField(max_length=11, unique=True) #Unique application number (Format : YYYYMMDDNNN)
    candidate_firstname = models.CharField(max_length=50) #Candidate's Firstname
    candidate_lastname = models.CharField(max_length=50) #Candidates's Lastname
    candidate_mail = models.CharField(max_length=100) #Candidates's Mail
    candidate_phone = models.CharField(max_length=10) #Candidates's Phone Number (French Format)
    candidate_password = models.CharField(max_length=200) #Candidate's hashed password
    post_id = models.IntegerField() # ID of the job offer
    creation_date = models.DateTimeField(auto_now_add=True) #Creation Date


