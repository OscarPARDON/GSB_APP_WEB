from django.contrib.auth.models import User # Import Django user module
from django.db import models # Import Django Model Module
#######################################################################################################################

class Publication(models.Model): # Publication / Jon Offer Model
    title = models.CharField(max_length=100) # Title of the publication / job offer
    description = models.TextField(max_length=500) # Description of the publication / job offer
    creation_date = models.DateTimeField(auto_now_add=True) # Creation Date of the publication / job offer
    created_by = models.ForeignKey(User, on_delete=models.CASCADE) # ID of the employee that created the publication / job offer
