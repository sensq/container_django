"""
WSGI config for mysite project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

prj_name = os.environ.get("DJANGO_PROJECT_NAME")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', (prj_name + '.settings'))

application = get_wsgi_application()
