"""
WSGI config for mehran_wifi project.
"""
import os
import sys
import traceback
from pathlib import Path

def create_error_wsgi_app(error_msg):
    def error_app(environ, start_response):
        status = '200 OK'
        headers = [('Content-type', 'text/plain; charset=utf-8')]
        start_response(status, headers)
        return [error_msg.encode('utf-8')]
    return error_app

try:
    # Add project root to sys.path so Vercel can resolve local modules and apps
    BASE_DIR = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(BASE_DIR))

    # Fix for Vercel's outdated SQLite version
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
except Exception as e:
    error_msg = f"Failed to load WSGI application:\n\n{traceback.format_exc()}"
    application = create_error_wsgi_app(error_msg)
    app = application
