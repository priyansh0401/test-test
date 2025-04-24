import os
import sys

# Add the project root to the Python path
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.append(path)

# Set the Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.guardian_eye.settings")

# Import Django and set up the WSGI application
import django
django.setup()

# Import the WSGI application
from backend.guardian_eye.wsgi import application

# Export the app for Vercel
app = application
