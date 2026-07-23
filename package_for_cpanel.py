import os
import zipfile
import secrets

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(PROJECT_ROOT, '..', 'schones-heim-cpanel.zip')

EXCLUDE = {
    '__pycache__', '.git', '.venv', 'venv', 'env',
    'construction_db', 'db.sqlite3', '*.sqlite3',
    'test_notification.py', 'test_server.py', 'validate.py',
    'logins.txt', 'node_modules', '.idea', '.vscode',
    'schones-heim-cpanel.zip', 'schones-heim-deployment.zip',
    'deploy.py', 'deploy_sftp.py', 'docker-compose.yml',
    'Dockerfile', 'Procfile', 'render.yaml',
    'debug_context.html',
}

def should_exclude(name):
    for p in EXCLUDE:
        if p.startswith('*') and name.endswith(p[1:]):
            return True
        if name == p:
            return True
    return False

# Generate a secure production secret key
prod_secret = secrets.token_urlsafe(50)

print("Creating cPanel deployment package...")

with zipfile.ZipFile(OUTPUT, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(PROJECT_ROOT):
        dirs[:] = [d for d in dirs if not should_exclude(d)]
        for f in files:
            if should_exclude(f):
                continue
            fp = os.path.join(root, f)
            arc = os.path.relpath(fp, PROJECT_ROOT)
            zipf.write(fp, arc)

    # Add .env.production with generated secret key
    env_content = f"""# Production Environment - Auto-generated
SECRET_KEY={prod_secret}
DEBUG=False
DB_ENGINE=django.db.backends.mysql
DB_NAME=wlsihszp_schones
DB_USER=wlsihszp
DB_PASSWORD=Me32323383#&
DB_HOST=localhost
DB_PORT=3306
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
"""
    zipf.writestr('.env', env_content)

    # Add setup.sh for server setup
    setup_sh = """#!/bin/bash
echo "=== SCHONES HEIM BUILDERS - Server Setup ==="

# Install requirements
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Seed data
python seed_data.py

# Collect static
python manage.py collectstatic --noinput

# Create superuser
echo "Creating admin superuser..."
python -c "
import os, django
os.environ['DJANGO_SETTINGS_MODULE']='config.settings'
django.setup()
from apps.core.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'schonesheimbuilders@gmail.com', 'Admin123!')
    print('Admin superuser created!')
else:
    print('Admin user already exists.')
"

echo "=== Setup Complete! ==="
echo "Restart your Python App in cPanel"
"""
    zipf.writestr('setup.sh', setup_sh)

size = os.path.getsize(OUTPUT) / 1024 / 1024
print(f"\nCreated: {OUTPUT}")
print(f"Size: {size:.2f} MB")
print(f"\n.env is pre-configured with:")
print(f"  DB_NAME=wlsihszp_schones")
print(f"  DB_USER=wlsihszp")
print(f"  DB_PASSWORD=Me32323383#&")
print(f"  SECRET_KEY=auto-generated")
print(f"\nAfter upload, update ALLOWED_HOSTS in .env with your actual domain!")
