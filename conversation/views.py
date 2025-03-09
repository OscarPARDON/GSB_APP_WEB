import base64
from secrets import token_hex
from django.shortcuts import render, redirect
from DjangoProject1.settings import MSG_ENC_TOKEN
from candidate.models import Application
from conversation.forms import MessageForm, InterviewForm, EditInterviewStatusForm, DelInterviewForm
from conversation.models import Thread, Message, Interview
from employee.models import Employee
from cryptography.fernet import Fernet
from mailing.wsgi import send_email, generate_ics_event
#####################################################################################################

# Function to assemble the encryption / decryption key of the conversation
def get_encryption_key(thread):
    raw_key = (thread.encryption_token + MSG_ENC_TOKEN).encode() # Assemble the unique conversation key with the static encryption key
    return base64.urlsafe_b64encode(raw_key[:32])  # Generation of a fernet key

# Function to encrypt the content of a message
def encrypt_message(content, key):
    fernet = Fernet(key) # Creation of a fernet key with the key
    return fernet.encrypt(content.encode()).decode()  # Encrypt the content

# Function to decrypt the content of a message
def decrypt_message(content, key):
    fernet = Fernet(key) # Creation of a fernet key with the key
    return fernet.decrypt(content.encode()).decode()  # Decrypt the content

#####################################################################################################

# This view manage the employees side of the chat
def employee_chat(request):
    candidateId = request.GET.get('candidateId', '') # Get the id of the candidate to chat with

    if not candidateId or not (candidateId.isdigit() and Application.objects.filter(application_number=candidateId).exists()): # If the candidate id is not valid ...
        return redirect('/employee/logout') # Kick the user

    candidate = Application.objects.get(application_number=candidateId) # Get the candidate
    employee = Employee.objects.get(id=request.user.id) # Get the employee

    if candidate.status == 4 : # If the application is archived ...
        return redirect('/employee/archived_applications') # Redirect to the archive

    if not Thread.objects.filter(candidate_id=candidate.application_number, employee_id=employee.id).exists(): # If the thread doesn't already exist ...
        thread = Thread(
            encryption_token=token_hex(16),
            candidate_id=candidate.application_number,
            employee_id=employee.id,
        )
        thread.save() # Create a new thread

    thread = Thread.objects.get(candidate_id=candidate.application_number, employee_id=employee.id) # Get the thread
    encryption_key = get_encryption_key(thread) # Get the encryption / decryption key of the conversation

    messages = Message.objects.filter(thread=thread).order_by('timestamp') # Get all the messages of the thread
    interviews = Interview.objects.filter(thread=thread).order_by('timestamp') # Get all the interviews of the thread

    feed = list(messages) + list(interviews) # Merge the message and the interviews to create the conversation feed
    feed.sort(key=lambda item: item.timestamp) # Sort the feed chronologically

    for item in feed: # For each item in the feed ...
        if isinstance(item, Message): # If the item is a message ...
            if item.is_read == 0 and item.sender == "candidate": # If the message was not seen before ...
                item.is_read = 1 # Set the message to read
                item.save()
            try: # Try to decrypt the message
                item.content = decrypt_message(item.content, encryption_key)
            except Exception: # Or display an error content
                item.content = "[Message corrompu ou clé incorrecte]"

    interviews = Interview.objects.filter(thread=thread,status=2).order_by('timestamp')[:5] # Get the last 5 validated interviews

    if request.method == 'POST': # If a message was sent
        plaintext_content = request.POST['contentField'] # Get the content of the message
        encrypted_content = encrypt_message(plaintext_content, encryption_key) # Encrypt the content
        message = Message(
            content=encrypted_content,
            thread=thread,
            sender="employee"
        )
        message.save() # Save the message in the database
        return redirect(f'/chat/employee?candidateId={candidateId}') # Redirect immediately to the chat
    else:
        error = request.GET.get("error","") # If an error occur while creating an interview, get the error, else do nothing
        msgform = MessageForm() # Get the message field
        interviewform = InterviewForm() # Get the interview creation form
        delinterviewform = DelInterviewForm() # Get the interview deletion form

    return render(request, 'employee_chat.html', {'feed': feed, 'application': candidate, 'msgform': msgform,'interviewform': interviewform,'interviews':interviews, 'delinterviewform':delinterviewform,"error":error}) # Call the chat page

# This view manage the candidates' side of the chat
def candidate_chat(request):
    employeeId = request.GET.get('employeeId', '') # Get the ID of the employee to chat with

    if not employeeId or not (employeeId.isdigit() and Employee.objects.filter(id=employeeId).exists()): # If the ID is not valid ...
        return redirect('/candidate/logout') # Kick the user out

    employee = Employee.objects.get(id=employeeId) # Get the employee
    if Thread.objects.filter(candidate=request.user.application_number,employee=employee.id).exists(): # If the conversation exists ...
        thread = Thread.objects.get(candidate=request.user.application_number, employee=employee.id)  # Get the conversation
    else : # If the conversation doesn't exists ...
        return redirect("/candidate/hub") # Redirect to the candidates' main page

    encryption_key = get_encryption_key(thread) # Get the encryption key of the conversation

    messages = Message.objects.filter(thread=thread).order_by('timestamp') # Get the messages of the conversation
    interviews = Interview.objects.filter(thread=thread).order_by('timestamp') # Get the interviews of the application

    feed = list(messages) + list(interviews) # Merge the interviews and the messages into one feed
    feed.sort(key=lambda item: item.timestamp) # Sort the feed chronologically

    for item in feed: # For each item in the feed
        if isinstance(item, Message): # If the item is a message ...
            if item.is_read == 0 and item.sender == "employee": # If the message was not seen ...
                item.is_read = 1 # Set it to read ...
                item.save()
            try: # Try to decrypt the message
                item.content = decrypt_message(item.content, encryption_key) # Message content decryption
            except Exception: # Or display an error message
                item.content = "[Message corrompu ou clé incorrecte]"
        else : # If the item is an interview ...
            if item.is_read == 0: # If the interview was not seen ...
                item.is_read = 1 # Set it to read
                item.save()

        interviews = Interview.objects.filter(thread=thread,status=2).order_by('date')[:3] # Get the last 3 validated interviews

    if request.method == 'POST': # If a message was sent
        msgform = MessageForm(request.POST) # Get the message form

        if msgform.is_valid(): # If the form is valid
            plaintext_content = request.POST['contentField'] # Get the content of the message
            encrypted_content = encrypt_message(plaintext_content, encryption_key) # Encrypt the content of the message

            message = Message(
                content=encrypted_content,
                thread=thread,
                sender="candidate"
            )
            message.save() # Save the message in the database
            return redirect(f'/chat/candidate?employeeId={employeeId}') # Redirect immediately to the chat

    msgform = MessageForm() # Get the message field
    editinterviewstatusform = EditInterviewStatusForm() # Get the form to interact with interviews
    return render(request, 'candidate_chat.html', {'messages': feed, "employee": employee, 'msgform': msgform, 'editinterviewstatusform':editinterviewstatusform,'interviews':interviews}) # Call the chat page

# This view manage the deletion of an interview
def delete_interview(request):
    if request.user.role in ["admin","manager"]: # If the user is an admin or a manager ...
        if request.method == 'POST': # If a deletion form was received
            form = DelInterviewForm(request.POST) # Get the form
            if form.is_valid(): # If the form is valid ...
                interviewId = form.cleaned_data['interviewId'] # Get the interview id

                # Check that the thread is valid
                threads = Thread.objects.filter(employee_id=request.user.id) # Get all the threads of the employee
                thread_check = 0 # Validation boolean
                for thread in threads: # For each thread
                    if Interview.objects.filter(thread=thread, id=int(interviewId)).exists(): # Check if the thread contains the interview
                        thread_check = 1 # The interview ID is valid

                if not thread_check: # The interview ID is not valid ...
                    return redirect("/employee/logout") # Kick the user
                interview = Interview.objects.get(id=interviewId) # Get the interview
                interview.delete() # Delete the interview
                if interview.status == 2: # If the interview was already accepted ...
                    candidate = Application.objects.get(application_number=interview.thread.candidate_id) # Get the candidate
                    send_email("interview_cancellation_email.html",{"interview":interview},[candidate.candidate_mail]) # Send an email to inform that the interview was cancelled

    previous_url = request.META.get('HTTP_REFERER', '/')
    return redirect(previous_url) # Return to the chat

# This view manages the creation of interviews
def new_interview(request):
    candidate_id = request.GET.get('candidateId', '') # Get the candidate's ID
    if candidate_id and candidate_id.isdigit() and Application.objects.filter(application_number=candidate_id).exists() : # If the ID is valid ...
        if Application.objects.get(application_number=candidate_id).status == 4: # If the application is archived ...
            return redirect('/employee/archived_applications') # Redirect to the archive page
        if Thread.objects.filter(candidate_id=candidate_id, employee_id=request.user.id).exists(): # If the thread exists ...
            thread = Thread.objects.get(candidate_id=candidate_id, employee_id=request.user.id) # Get the thread
            if request.method == 'POST': # If the creation form is received ...
                form = InterviewForm(request.POST) # Get the form
                if form.is_valid(): # If the form is valid ...

                    # Check that the thread is valid
                    threads = Thread.objects.filter(employee_id=thread.employee_id).union(Thread.objects.filter(candidate_id=thread.candidate_id)) # Get the threads
                    for element in threads: # For each thread
                        if Interview.objects.filter(thread=element, date=str(form.cleaned_data['date']) + ' ' + str(form.cleaned_data['time'])).exists(): # Check if another thread is scheduled on the same time ...
                            return redirect(f"/chat/employee?candidateId={candidate_id}&error=L'un où les deux participants sont déjà occupés !") # Send back to the chat page with the informative error

                    interview = Interview(
                        thread = thread,
                        date = str(form.cleaned_data['date']) + ' ' + str(form.cleaned_data['time']),
                        is_read = 0,
                        status = 0,
                        title = form.cleaned_data['title'],
                        interview_category = form.cleaned_data['category'],
                    )
                    interview.save() # Save the interview in the database
            return redirect(f"/chat/employee?candidateId={candidate_id}") # Redirect to the chat
    return redirect('/employee/validated_applications') # Redirect to the validated applications page

# This view manage the interactions with the interviews
def update_interview_status(request):
    if request.method == 'POST': # If a status modification form was received
        form = EditInterviewStatusForm(request.POST) # Get the form
        if form.is_valid(): # If the form is valid ...
            interviewId = form.cleaned_data['interviewId'] # Get the interview id
            status = form.cleaned_data['status'] # Get the new status

            # Interview id verification
            threads = Thread.objects.filter(candidate_id=request.user.application_number) # Get the threads
            thread_check = 0 # Validation boolean
            for thread in threads: # For each thread
                if Interview.objects.filter(thread=thread,id=int(interviewId)).exists(): # If the thread contains the interview
                    thread_check = 1 # The interview is valid

            if not thread_check: # The interview is not valid
                return redirect("/candidate/logout") # Kick the user

            interview = Interview.objects.get(id=interviewId) # Get the interview
            interview.status = status
            interview.save() # Update the status

            if status == 2: # If the interview is accepted
                employee = Employee.objects.get(id=interview.thread.employee_id) # Get the employee
                ics_content = generate_ics_event(interview) # Create an Agenda Event
                send_email("change_interview_status_email.html",{"interview":interview},[employee.employee_email,request.user.candidate_mail],ics_content) # Send an email to confirm the interview with the agenda event

    previous_url = request.META.get('HTTP_REFERER', '/')
    return redirect(previous_url) # Redirect to the chat page
