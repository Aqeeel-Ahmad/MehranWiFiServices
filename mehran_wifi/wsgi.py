"""
WSGI config for mehran_wifi project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

# Add project root to sys.path so Vercel can resolve local modules and apps
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Fix for Vercel's outdated SQLite version (AWS Lambda uses SQLite 3.7.17, Django 5+ requires 3.31.0+)
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mehran_wifi.settings')

application = get_wsgi_application()
app = application
