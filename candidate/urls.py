from django.urls import path # Import Django Url Module
from . import views # Import Django Views Module
##############################################################################################################

urlpatterns = [
    path('',views.candidate_hub,name='default'), #By default, try to display the main candidate page
    path('login', views.candidate_login, name='candidate_login'), # Login Form
    path('hub', views.candidate_hub, name='candidate_hub'), # Main page for candidates
    path('logout', views.candidate_logout, name='candidate_logout'), # Path used to Log out the user
    path('show_file', views.show_file, name='candidate_show_file'), # Path to display the candidate file
    path('delete', views.candidate_delete, name='candidate_delete'), # Path to delete the application
    path('update', views.candidate_update, name='candidate_update'), # Form to update the application data
]