import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.forms import DateInput

from candidate.models import Application
from conversation.models import Interview, Thread


class MessageForm(forms.Form):
    contentField = forms.CharField(max_length=300,widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Entrez votre message'}))

class InterviewForm(forms.Form):

    title = forms.CharField(max_length=50,widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Entrez un cours titre'}))
    date = forms.DateField(widget=DateInput(attrs={'class':'form-control','type':'date','min': datetime.date.today().isoformat()}))
    time = forms.TimeField(widget=forms.TimeInput(attrs={'class':'form-control','type':'time',"min":"07:00","max":"19:00"}))
    category = forms.ChoiceField(choices=[('Préliminaire',"Préliminaire"),('Technique','Technique'),('Administratif','Administratif'),('Autre','Autre')],widget=forms.Select(attrs={'class':'form-control'}))

    def clean(self):
        cleaned_data =super().clean()

        interview_date = cleaned_data.get("date")
        if interview_date < datetime.date.today():
            raise ValidationError("La date de l'entretien ne peux pas être inférieure à la date d'aujourd'hui")

        interview_time = cleaned_data.get("time")
        min_time = datetime.time(7, 0)  # 07:00
        max_time = datetime.time(19, 0)  # 19:00

        if not (min_time <= interview_time <= max_time):
            raise forms.ValidationError("L'heure de l'entretien doit être comprise entre 07:00 et 19:00.")

class EditInterviewStatusForm(forms.Form):
    interviewId = forms.IntegerField(widget=forms.HiddenInput(attrs={'id':'interviewId'}))
    status = forms.IntegerField(widget=forms.HiddenInput(attrs={'id':'status'}))

    def clean(self):
        cleaned_data = super().clean()
        interviewId = cleaned_data.get('interviewId')
        status = cleaned_data.get('status')

        if not Interview.objects.filter(id=interviewId).exists():
            raise ValidationError("Element Entretien Inconnu")

        if Interview.objects.get(id=interviewId).status != 0 :
            raise ValidationError("Cet Element Entretien n'est pas modifiable")

        if status not in [1,2]:
            raise ValidationError("Nouveau Status Invalide")

class DelInterviewForm(forms.Form):
    interviewId = forms.IntegerField(widget=forms.HiddenInput(attrs={'id': 'interviewId'}))

    def clean(self):
        cleaned_data = super().clean()
        interviewId = cleaned_data.get('interviewId')

        if not Interview.objects.filter(id=interviewId,).exists():
            raise ValidationError("Element Entretien Inconnu")

