#!/usr/bin/env python
"""
SCHONES HEIM BUILDERS - One-Click Server Setup
Run this file from cPanel Python App console or SSH.
It handles everything: migrations, seed data, static files, admin user.
"""
import os
import sys
import subprocess

# Ensure we're in the right directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

def run(cmd):
    print(f"\n>> {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result.returncode == 0

def main():
    print("=" * 60)
    print("  SCHONES HEIM BUILDERS - Server Setup")
    print("=" * 60)

    # Step 1: Install requirements
    print("\n[1/5] Installing Python packages...")
    run(f"{sys.executable} -m pip install -r requirements.txt -q")

    # Step 2: Run migrations
    print("\n[2/5] Running database migrations...")
    run(f"{sys.executable} manage.py migrate")

    # Step 3: Seed data
    print("\n[3/5] Seeding database...")
    run(f"{sys.executable} seed_data.py")

    # Step 4: Collect static files
    print("\n[4/5] Collecting static files...")
    import shutil
    if os.path.exists('staticfiles'):
        shutil.rmtree('staticfiles')
        print("  Cleared old staticfiles cache")
    run(f"{sys.executable} manage.py collectstatic --noinput")

    # Step 5: Create superuser if not exists
    print("\n[5/5] Ensuring admin superuser exists...")
    import django
    django.setup()
    from apps.core.models import User
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'schonesheimbuilders@gmail.com', 'Admin123!')
        print("  Admin superuser created! (admin / Admin123!)")
    else:
        print("  Admin user already exists.")

    print("\n" + "=" * 60)
    print("  SETUP COMPLETE!")
    print("=" * 60)
    print("\n  Login: admin / Admin123!")
    print("  Restart your Python App in cPanel to apply changes.")
    print("=" * 60)

if __name__ == '__main__':
    main()
