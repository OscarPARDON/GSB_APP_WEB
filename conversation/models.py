from django.db import models

from candidate.models import Application
from employee.models import Employee


class Thread(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Application, on_delete=models.CASCADE)
    encryption_token = models.CharField(max_length=16)

class Message(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    content = models.TextField(max_length=300)
    sender = models.CharField(max_length=10,default='candidate')
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

class Interview(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    status = models.IntegerField(default=0)
    title = models.CharField(max_length=100, default='Entretien')
    date = models.DateTimeField(default="2000-01-01")
    interview_category = models.CharField(max_length=100, default='Autre')