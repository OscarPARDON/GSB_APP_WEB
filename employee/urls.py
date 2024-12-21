from django.urls import path # Import Django Url Module
from . import views # Import Django Views Module
###################################################################################################

urlpatterns = [
    path('', views.employee_hub, name='default'), # Default : try to redirect to the employee main page

    path('hub',views.employee_hub, name='employee_hub'), # Main page for employee

    path('login',views.employee_login, name='employee_login'), # Employee's login page

    path('logout', views.employee_logout, name='employee_logout'), # Path to log the employee out

    path('show_file', views.show_file, name='employee_show_file'), # Path to display the asked file

    path('offer_applications', views.offer_applications, name='offer_applications'), # Page that shows all the applications of an offer

    path('status_modification', views.status_modification, name='status_modification'), # Path to modify the status of an application

]