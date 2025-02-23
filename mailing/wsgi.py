import threading
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.db import close_old_connections

from datetime import datetime, timedelta
from django.utils.timezone import make_aware


from datetime import timedelta
from django.utils.timezone import make_aware

def generate_ics_event(interview):
    # S'assurer que la date est en timezone-aware
    event_start = make_aware(interview.date) if interview.date.tzinfo is None else interview.date
    event_end = event_start + timedelta(hours=1)  # Par défaut, durée de 1 heure

    # Format des dates en iCalendar (UTC)
    dtstamp = event_start.strftime("%Y%m%dT%H%M%SZ")
    dtstart = event_start.strftime("%Y%m%dT%H%M%SZ")
    dtend = event_end.strftime("%Y%m%dT%H%M%SZ")

    event_details = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//GSB Recrutement//Entretien//FR
BEGIN:VEVENT
UID:{interview.id}@gsb.recrutement.com
DTSTAMP:{dtstamp}
DTSTART:{dtstart}
DTEND:{dtend}
SUMMARY:{interview.title}
DESCRIPTION: Entretien {interview.interview_category}.
LOCATION: Paris, France
END:VEVENT
END:VCALENDAR"""

    return event_details

def send_email(template_name: str, template_vars: dict, emails: list, ics_content = False):
    def email_task():
        try:
            close_old_connections()
            html_content = render_to_string(template_name, template_vars)
            email = EmailMessage(
                subject="GSB Recrutement",
                body=html_content,
                from_email=settings.EMAIL_HOST_USER,
                to=emails
            )
            email.content_subtype = 'html'
            if ics_content:
                email.attach("invitation.ics",ics_content,"text/calendar")
            email.send(fail_silently=True)
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email : {e}")

    thread = threading.Thread(target=email_task)
    thread.start()
