"""Vercel serverless entry – routes all traffic to Django."""
import os

os.environ.setdefault('VERCEL', '1')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

from core.wsgi import app  # noqa: E402, F401
