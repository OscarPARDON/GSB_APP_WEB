import os # Import os management module
from django.core.wsgi import get_wsgi_application # Import Django WSGI Module
###################################################################################################################

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject1.settings') # Set default settings
application = get_wsgi_application() # Create application
