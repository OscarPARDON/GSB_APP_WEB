from django.apps import AppConfig # Import Django app configuration module
####################################################################################################################

# Configuration of the Candidate App
class CandidateConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'candidate'
