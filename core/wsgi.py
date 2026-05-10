"""
WSGI config for cashier project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os
import collections
import collections.abc

# Compatibility patch for Python 3.10+ (django-3-jet uses deprecated collections classes)
for attr in ('MutableSet', 'MutableMapping', 'MutableSequence', 'Mapping', 'Callable'):
    if not hasattr(collections, attr):
        setattr(collections, attr, getattr(collections.abc, attr))

from django.core.wsgi import get_wsgi_application


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()
app = application