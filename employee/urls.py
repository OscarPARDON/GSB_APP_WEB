from django.urls import path # Import Django Url Module
from . import views # Import Django Views Module
###################################################################################################

urlpatterns = [
    path('', views.application_management, name='default'), # Default : try to redirect to the employee main page
    path('hub',views.employee_hub, name='employee_hub'), # Main page for employee
    path('login',views.employee_login, name='employee_login'), # Employee's login page
    path('logout', views.employee_logout, name='employee_logout'), # Path to log the employee out
    path('show_file', views.show_file, name='employee_show_file'), # Path to display the asked file
    path('offer_applications', views.offer_applications, name='offer_applications'), # Page that shows all the applications of an offer
    path('status_modification', views.status_modification, name='status_modification'), # Path to modify the status of an application
    path('application_management', views.application_management, name='application_management'), # Path to the admin menu
    path('admin_user_management',views.admin_user_management, name='user_management'), # Path to the user management page
    path('delete', views.employee_delete, name='employee_delete'), # Page to delete an employee
    path('new_employee', views.new_employee, name='new_employee'), # Path to create an employee
    path('update', views.employee_update, name='employee_update'), # Path to update an employee
    path('admin_publication_management', views.admin_publication_management, name='publication_management'), # Path to the publication manager page
    path('new_publication', views.new_publication, name='new_publication'), # Path to create a publication
    path('delete_publication', views.delete_publication, name='delete_publication'), # Page to delete a publication
    path('update_publication', views.publication_update, name='update_publication'), # Page to update a publication
    path('change_password', views.employee_change_password, name='employee_change_password'), # Page to change password
    path('reset_password', views.reset_employee_password, name='employee_reset_password'), # Path to reset an employee's password
    path('validated_applications', views.validated_applications, name='validated_applications'), # Page to access to validated applications
    path('archive_publication', views.archive_publication, name='archive_publication'),  # Path to archive a publication
    path('archived_applications', views.archived_applications, name='archived_applications'), # Archive page
    path('archived_application_info', views.archived_application_info, name='archived_application_info'), # Page that display the detail of an archived application
    path('application_delete',views.application_delete, name='delete_application'), # Path to delete an application
]