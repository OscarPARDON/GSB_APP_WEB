from django.urls import path
from . import views

urlpatterns = [
    path('', views.visitorpage, name='visitorpage'), # By default, send the user on the visitor view
    path('application', views.application, name='application'), # View to manage application submissions to a job offer
    path('application_success', views.application_success, name='application_success'), # View to manage successful applications submission

]