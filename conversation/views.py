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


def get_encryption_key(thread):
    raw_key = (thread.encryption_token + MSG_ENC_TOKEN).encode()
    return base64.urlsafe_b64encode(raw_key[:32])  # La clé doit être de 32 bytes pour Fernet

def encrypt_message(content, key):
    fernet = Fernet(key)
    return fernet.encrypt(content.encode()).decode()  # Retourne une chaîne encodée en base64

def decrypt_message(content, key):
    fernet = Fernet(key)
    return fernet.decrypt(content.encode()).decode()  # Retourne une chaîne en clair

def employee_chat(request):
    candidateId = request.GET.get('candidateId', '')

    if not candidateId or not (candidateId.isdigit() and Application.objects.filter(application_number=candidateId).exists()):
        return redirect('/employee/logout')

    candidate = Application.objects.get(application_number=candidateId)
    employee = Employee.objects.get(id=request.user.id)

    if candidate.status == 4 :
        return redirect('/employee/archived_applications')

    if not Thread.objects.filter(candidate_id=candidate.application_number, employee_id=employee.id).exists():
        thread = Thread(
            encryption_token=token_hex(16),
            candidate_id=candidate.application_number,
            employee_id=employee.id,
        )
        thread.save()

    thread = Thread.objects.get(candidate_id=candidate.application_number, employee_id=employee.id)
    encryption_key = get_encryption_key(thread)

    # Récupération des messages et des interviews
    messages = Message.objects.filter(thread=thread).order_by('timestamp')
    interviews = Interview.objects.filter(thread=thread).order_by('timestamp')

    # Fusion des deux listes et tri par timestamp
    feed = list(messages) + list(interviews)
    feed.sort(key=lambda item: item.timestamp)

    # Déchiffrement et mise à jour des messages non lus
    for item in feed:
        if isinstance(item, Message):
            if item.is_read == 0 and item.sender == "candidate":
                item.is_read = 1
                item.save()
            try:
                item.content = decrypt_message(item.content, encryption_key)
            except Exception:
                item.content = "[Message corrompu ou clé incorrecte]"

    interviews = Interview.objects.filter(thread=thread,status=2).order_by('timestamp')[:5]

    if request.method == 'POST':
        plaintext_content = request.POST['contentField']
        encrypted_content = encrypt_message(plaintext_content, encryption_key)
        message = Message(
            content=encrypted_content,
            thread=thread,
            sender="employee"
        )
        message.save()
        return redirect(f'/chat/employee?candidateId={candidateId}')
    else:
        error = request.GET.get("error","")
        msgform = MessageForm()
        interviewform = InterviewForm()
        delinterviewform = DelInterviewForm()

    return render(request, 'employee_chat.html', {'feed': feed, 'application': candidate, 'msgform': msgform,'interviewform': interviewform,'interviews':interviews, 'delinterviewform':delinterviewform,"error":error})


def candidate_chat(request):
    employeeId = request.GET.get('employeeId', '')

    if not employeeId or not (employeeId.isdigit() and Employee.objects.filter(id=employeeId).exists()):
        return redirect('/candidate/logout')

    employee = Employee.objects.get(id=employeeId)
    if Thread.objects.filter(candidate=request.user.application_number,employee=employee.id).exists():
        thread = Thread.objects.get(candidate=request.user.application_number, employee=employee.id)
    else :
        return redirect("/candidate/hub")
    encryption_key = get_encryption_key(thread)

    messages = Message.objects.filter(thread=thread).order_by('timestamp')
    interviews = Interview.objects.filter(thread=thread).order_by('timestamp')

    # Fusion des deux listes et tri par timestamp
    feed = list(messages) + list(interviews)
    feed.sort(key=lambda item: item.timestamp)

    # Déchiffrement et mise à jour des messages non lus
    for item in feed:
        if isinstance(item, Message):
            if item.is_read == 0 and item.sender == "employee":
                item.is_read = 1
                item.save()
            try:
                item.content = decrypt_message(item.content, encryption_key)
            except Exception:
                item.content = "[Message corrompu ou clé incorrecte]"
        else :
            if item.is_read == 0:
                item.is_read = 1
                item.save()

        interviews = Interview.objects.filter(thread=thread,status=2).order_by('date')[:3]

    if request.method == 'POST':
        msgform = MessageForm(request.POST)

        if msgform.is_valid():
            plaintext_content = request.POST['contentField']
            encrypted_content = encrypt_message(plaintext_content, encryption_key)

            message = Message(
                content=encrypted_content,
                thread=thread,
                sender="candidate"
            )
            message.save()
            return redirect(f'/chat/candidate?employeeId={employeeId}')

    msgform = MessageForm()
    editinterviewstatusform = EditInterviewStatusForm()
    return render(request, 'candidate_chat.html', {'messages': feed, "employee": employee, 'msgform': msgform, 'editinterviewstatusform':editinterviewstatusform,'interviews':interviews})

def delete_interview(request):
    if request.user.role in ["admin","manager"]:
        if request.method == 'POST':
            form = DelInterviewForm(request.POST)
            if form.is_valid():
                interviewId = form.cleaned_data['interviewId']

                threads = Thread.objects.filter(employee_id=request.user.id)
                thread_check = 0
                for thread in threads:
                    if Interview.objects.filter(thread=thread, id=int(interviewId)).exists():
                        thread_check = 1

                if not thread_check:
                    return redirect("/employee/logout")
                interview = Interview.objects.get(id=interviewId)
                interview.delete()
                if interview.status == 2:
                    candidate = Application.objects.get(application_number=interview.thread.candidate_id)
                    send_email("interview_cancellation_email.html",{"interview":interview},[candidate.candidate_mail])

    previous_url = request.META.get('HTTP_REFERER', '/')
    return redirect(previous_url)

def new_interview(request):
    candidate_id = request.GET.get('candidateId', '')
    if candidate_id and candidate_id.isdigit() and Application.objects.filter(application_number=candidate_id).exists() :
        if Application.objects.get(application_number=candidate_id).status == 4:
            return redirect('/employee/archived_applications')
        if Thread.objects.filter(candidate_id=candidate_id, employee_id=request.user.id).exists():
            thread = Thread.objects.get(candidate_id=candidate_id, employee_id=request.user.id)
            if request.method == 'POST':
                form = InterviewForm(request.POST)
                if form.is_valid():

                    threads = Thread.objects.filter(employee_id=thread.employee_id).union(Thread.objects.filter(candidate_id=thread.candidate_id))
                    for element in threads:
                        if Interview.objects.filter(thread=element, date=str(form.cleaned_data['date']) + ' ' + str(form.cleaned_data['time'])).exists():
                            return redirect(f"/chat/employee?candidateId={candidate_id}&error=L'un où les deux participants sont déjà occupés !")

                    interview = Interview(
                        thread = thread,
                        date = str(form.cleaned_data['date']) + ' ' + str(form.cleaned_data['time']),
                        is_read = 0,
                        status = 0,
                        title = form.cleaned_data['title'],
                        interview_category = form.cleaned_data['category'],
                    )
                    interview.save()
            return redirect(f"/chat/employee?candidateId={candidate_id}")
    return redirect('/employee/validated_applications')

def update_interview_status(request):
    if request.method == 'POST':
        form = EditInterviewStatusForm(request.POST)
        if form.is_valid():
            interviewId = form.cleaned_data['interviewId']
            status = form.cleaned_data['status']

            threads = Thread.objects.filter(candidate_id=request.user.application_number)
            thread_check = 0
            for thread in threads:
                if Interview.objects.filter(thread=thread,id=int(interviewId)).exists():
                    thread_check = 1

            if not thread_check:
                return redirect("/candidate/logout")

            interview = Interview.objects.get(id=interviewId)
            interview.status = status
            interview.save()

            if status == 2:
                employee = Employee.objects.get(id=interview.thread.employee_id)
                ics_content = generate_ics_event(interview)
                send_email("change_interview_status_email.html",{"interview":interview},[employee.employee_email,request.user.candidate_mail],ics_content)

    previous_url = request.META.get('HTTP_REFERER', '/')
    return redirect(previous_url)
