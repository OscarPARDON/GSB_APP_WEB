import threading
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.db import close_old_connections
from datetime import timedelta
from django.utils.timezone import make_aware
##########################################################################################

# This function generates an agenda event for the interview
def generate_ics_event(interview):

    event_start = make_aware(interview.date) if interview.date.tzinfo is None else interview.date
    event_end = event_start + timedelta(hours=1) # Set the event end to one hour after the starting hour

    dtstamp = event_start.strftime("%Y%m%dT%H%M%SZ") # Format & Convert time into string
    dtstart = event_start.strftime("%Y%m%dT%H%M%SZ") # Format & Convert time into string
    dtend = event_end.strftime("%Y%m%dT%H%M%SZ") # Format & Convert time into string

    # Create icalendar event
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

    return event_details # Return the icalendar element

# This function allow to send an email asynchronously
def send_email(template_name: str, template_vars: dict, emails: list, ics_content = False):
    def email_task(): # Create a task to execute asynchronously
        try:
            close_old_connections() # Close old threads
            html_content = render_to_string(template_name, template_vars) # Get the email content
            email = EmailMessage(
                subject="GSB Recrutement",
                body=html_content,
                from_email=settings.EMAIL_HOST_USER,
                to=emails
            ) # Create the email object
            email.content_subtype = 'html' # Set the content type to HTML
            if ics_content: # If the icalendar event was successfully created ...
                email.attach("invitation.ics",ics_content,"text/calendar") # Join the event to the email
            email.send(fail_silently=True) # Send the email (do nothing if error)
        except Exception as e: # If an error occur while creating or sending the email ...
            print(f"Erreur lors de l'envoi de l'email : {e}") # Display an error in the console

    thread = threading.Thread(target=email_task) # Create a new thread to send the email
    thread.start() # Execute the thread
