"""
WSGI config for cashier project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os
import shutil
import collections
import collections.abc

# Compatibility patch for Python 3.10+ (django-3-jet uses deprecated collections classes)
for attr in ('MutableSet', 'MutableMapping', 'MutableSequence', 'Mapping', 'Callable'):
    if not hasattr(collections, attr):
        setattr(collections, attr, getattr(collections.abc, attr))

import django.utils.encoding

if not hasattr(django.utils.encoding, 'python_2_unicode_compatible'):
    django.utils.encoding.python_2_unicode_compatible = lambda x: x

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Vercel serverless: copy SQLite DB to writable /tmp
if os.environ.get('VERCEL') or os.environ.get('VERCEL_ENV'):
    os.environ['VERCEL'] = '1'
    src_db = os.path.join(BASE_DIR, 'cashier.db')
    tmp_db = '/tmp/cashier.db'
    if os.path.exists(src_db):
        if not os.path.exists(tmp_db) or os.path.getmtime(src_db) > os.path.getmtime(tmp_db):
            shutil.copy2(src_db, tmp_db)
    os.environ['SQLITE_DB_PATH'] = tmp_db

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
app = application