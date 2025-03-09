from django.db import models

from candidate.models import Application
from employee.models import Employee

# Conversation Model
class Thread(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE) # The employee who participate in the conversation
    candidate = models.ForeignKey(Application, on_delete=models.CASCADE) # The candidate who participate in the conversation
    encryption_token = models.CharField(max_length=16) # Encryption key of the discussion

# Message Model
class Message(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE) # The conversation the message belongs in
    content = models.TextField(max_length=300) # The content of the message (encrypted)
    sender = models.CharField(max_length=10,default='candidate') # Sender of the message (employee or candidate)
    timestamp = models.DateTimeField(auto_now_add=True) # Time and date the message was sent
    is_read = models.BooleanField(default=False) # Boolean if the message was seen or not

# Interview Model
class Interview(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE) # The thread the interview belongs in
    timestamp = models.DateTimeField(auto_now_add=True) # The time and date the interview was created
    is_read = models.BooleanField(default=False) # Boolean if the interview was seen or not
    status = models.IntegerField(default=0) # status of the interview (0 = proposition, 1 = refused, 2 = accepted)
    title = models.CharField(max_length=100, default='Entretien') # Title of the interview input
    date = models.DateTimeField(default="2000-01-01") # Scheduled date for the interview
    interview_category = models.CharField(max_length=100, default='Autre') # Scheduled hour for the interview