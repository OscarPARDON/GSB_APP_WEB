from django.urls import path
from conversation import views

urlpatterns = [
    path('employee',views.employee_chat,name='employee_chat'),
    path('candidate',views.candidate_chat,name='candidate_chat'),
    path('new_interview',views.new_interview,name='new_interview'),
    path('delete_interview',views.delete_interview,name='delete_interview'),
    path('update_interview_status',views.update_interview_status,name='update_interview_status'),
]