"""
WSGI config for mehran_wifi project.
"""
import os
import sys
import traceback
from pathlib import Path

# Add project root to sys.path so Vercel can resolve local modules and apps
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mehran_wifi.settings')

_application = None
_error_msg = None

try:
    from django.core.wsgi import get_wsgi_application
    _application = get_wsgi_application()
except Exception:
    _error_msg = f"Failed to load WSGI application:\n\n{traceback.format_exc()}"

def application(environ, start_response):
    if _error_msg:
        status = '200 OK'
        headers = [('Content-type', 'text/plain; charset=utf-8')]
        start_response(status, headers)
        return [_error_msg.encode('utf-8')]
    return _application(environ, start_response)

app = application
