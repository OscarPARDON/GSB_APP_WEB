from django.urls import path
from conversation import views

urlpatterns = [
    path('employee',views.employee_chat,name='employee_chat'), # Path to the employees' chat page
    path('candidate',views.candidate_chat,name='candidate_chat'), # Path to the candidates' chat page
    path('new_interview',views.new_interview,name='new_interview'), # Path to create an interview
    path('delete_interview',views.delete_interview,name='delete_interview'), # Path to delete an interview
    path('update_interview_status',views.update_interview_status,name='update_interview_status'), # Path to update the status of an application
]