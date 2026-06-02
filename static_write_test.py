import os
import collections
import django
import django.utils.encoding as enc
from django.core.files.base import ContentFile

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

if not hasattr(collections, 'MutableSet'):
    import collections.abc
    collections.MutableSet = collections.abc.MutableSet
if not hasattr(collections, 'Mapping'):
    import collections.abc
    collections.Mapping = collections.abc.Mapping
if not hasattr(collections, 'Sequence'):
    import collections.abc
    collections.Sequence = collections.abc.Sequence
if not hasattr(collections, 'Iterable'):
    import collections.abc
    collections.Iterable = collections.abc.Iterable
if not hasattr(collections, 'Callable'):
    import collections.abc
    collections.Callable = collections.abc.Callable

enc.python_2_unicode_compatible = lambda x: x

django.setup()
from django.contrib.staticfiles.storage import staticfiles_storage
print('STATIC_ROOT', staticfiles_storage.location)
print('exists', staticfiles_storage.exists('test_collectstatic.txt'))
content = ContentFile(b'test')
path = staticfiles_storage.save('test_collectstatic.txt', content)
print('saved', path)
print('exists after', staticfiles_storage.exists('test_collectstatic.txt'))
print('file path', staticfiles_storage.path('test_collectstatic.txt'))
