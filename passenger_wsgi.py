import os
import sys

# PyMySQL compatibility (acts as MySQLdb)
import pymysql
pymysql.install_as_MySQLdb()

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Add project to Python path
project_home = os.path.dirname(os.path.abspath(__file__))
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Load environment variables
from decouple import config as decouple_config

# Set environment from .env file if it exists
env_path = os.path.join(project_home, '.env')
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip())

# Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
