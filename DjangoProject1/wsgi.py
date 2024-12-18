"""
WSGI config for DjangoProject1 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os # Import os management module
from django.core.wsgi import get_wsgi_application # Import Django WSGI Module
###################################################################################################################

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject1.settings') # Set default settings
application = get_wsgi_application() # Create application
