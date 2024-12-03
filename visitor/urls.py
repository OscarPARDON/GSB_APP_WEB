from django.urls import path
from . import views

urlpatterns = [
    path('', views.visitorpage, name='visitorpage'), # By default, send the user on the visitor page
    path('application', views.application, name='application'), # Page to submit an application to a job offer
    path('application_success', views.application_success, name='application_success'), # Page that inform the user that it's application was successfully sent

]