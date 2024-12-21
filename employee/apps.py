from django.apps import AppConfig # Import Django app configuration module
################################################################################################################

# Configuration of the Employee App
class EmployeeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'employee'
