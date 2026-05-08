#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# Monkeypatch for django-jet compatibility
import django.utils.encoding
if not hasattr(django.utils.encoding, 'python_2_unicode_compatible'):
    django.utils.encoding.python_2_unicode_compatible = lambda x: x

# Monkeypatch for collections.MutableSet compatibility (Python 3.10+)
import collections
if not hasattr(collections, 'MutableSet'):
    import collections.abc
    collections.MutableSet = collections.abc.MutableSet
    collections.MutableMapping = collections.abc.MutableMapping
    collections.Mapping = collections.abc.Mapping
    collections.Sequence = collections.abc.Sequence
    collections.Iterable = collections.abc.Iterable
    collections.Callable = collections.abc.Callable




def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
