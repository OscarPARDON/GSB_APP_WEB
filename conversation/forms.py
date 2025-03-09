import datetime
from django import forms
from django.core.exceptions import ValidationError
from django.forms import DateInput
from candidate.models import Application
from conversation.models import Interview, Thread
#######################################################################################################################

# This form is used to send messages
class MessageForm(forms.Form):
    contentField = forms.CharField(max_length=300,widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Entrez votre message'})) # Message input

# This form is used to create interviews
class InterviewForm(forms.Form):

    title = forms.CharField(max_length=50,widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Entrez un cours titre'})) # Title of the interview input
    date = forms.DateField(widget=DateInput(attrs={'class':'form-control','type':'date','min': datetime.date.today().isoformat()})) # Date of the interview input
    time = forms.TimeField(widget=forms.TimeInput(attrs={'class':'form-control','type':'time',"min":"07:00","max":"19:00"})) # Hour of the interview
    category = forms.ChoiceField(choices=[('Préliminaire',"Préliminaire"),('Technique','Technique'),('Administratif','Administratif'),('Autre','Autre')],widget=forms.Select(attrs={'class':'form-control'})) # Type of the interview

    def clean(self):
        cleaned_data =super().clean() # Get the values cleaned by the default function

        interview_date = cleaned_data.get("date") # Get the date of the interview
        if interview_date < datetime.date.today(): # Check that the date is not in the past or else ...
            raise ValidationError("La date de l'entretien ne peux pas être inférieure à la date d'aujourd'hui") # Raise form error

        interview_time = cleaned_data.get("time") # Get the time of the interview
        min_time = datetime.time(7, 0)  # Set the minimum interview hour to 7AM
        max_time = datetime.time(19, 0)  # Set the maximum interview hour to 7PM

        if not (min_time <= interview_time <= max_time): # If the interview hour is not in the stamp ...
            raise forms.ValidationError("L'heure de l'entretien doit être comprise entre 07:00 et 19:00.") # Raise form error

# This form is used to edit the status of an interview
class EditInterviewStatusForm(forms.Form):

    interviewId = forms.IntegerField(widget=forms.HiddenInput(attrs={'id':'interviewId'})) # ID of the interview input
    status = forms.IntegerField(widget=forms.HiddenInput(attrs={'id':'status'})) # Status of the interview input

    def clean(self):
        cleaned_data = super().clean() # Get the data cleaned by the default function
        interviewId = cleaned_data.get('interviewId') # Get the interview id
        status = cleaned_data.get('status') # Get the interview status

        if not Interview.objects.filter(id=interviewId).exists(): # If the interview doesn't exist ...
            raise ValidationError("Element Entretien Inconnu") # Raise form error

        if Interview.objects.get(id=interviewId).status != 0 : # If the status is other than 0 (waiting for the candidate's validation)
            raise ValidationError("Cet Element Entretien n'est pas modifiable") # Raise form error

        if status not in [1,2]: # If the new status is not between 1 (refused) and 2 (accepted) ...
            raise ValidationError("Nouveau Status Invalide") # Raise form error

# This form is used to delete an interview
class DelInterviewForm(forms.Form):

    interviewId = forms.IntegerField(widget=forms.HiddenInput(attrs={'id': 'interviewId'})) # Interview ID input

    def clean(self):
        cleaned_data = super().clean() # Get the data cleaned by the default function
        interviewId = cleaned_data.get('interviewId') # Get the interview id

        if not Interview.objects.filter(id=interviewId,).exists():  # If the interview doesn't exist ...
            raise ValidationError("Element Entretien Inconnu") #  Raise form error
