#!/usr/bin/env python
"""
SCHONES HEIM BUILDERS - One-Click Server Setup
Run: python setup.py
"""
import os
import sys
import subprocess
import shutil

os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

def run(cmd):
    print(f"\n>> {cmd}")
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0

def main():
    print("=" * 60)
    print("  SCHONES HEIM BUILDERS - Server Setup")
    print("=" * 60)

    print("\n[0/7] Cleaning old caches...")
    for d in ["staticfiles", "__pycache__"]:
        if os.path.exists(d):
            shutil.rmtree(d)
            print(f"  Removed: {d}/")
    for root, dirs, files in os.walk("."):
        for dirname in list(dirs):
            if dirname == "__pycache__":
                p = os.path.join(root, dirname)
                shutil.rmtree(p)
        for f in files:
            if f.endswith(".pyc"):
                os.remove(os.path.join(root, f))

    print("\n[1/7] Installing packages...")
    run(f"{sys.executable} -m pip install -r requirements.txt")

    print("\n[2/7] Running migrations...")
    run(f"{sys.executable} manage.py migrate")

    print("\n[3/7] Seeding database...")
    run(f"{sys.executable} seed_data.py")

    print("\n[4/7] Collecting static files...")
    run(f"{sys.executable} manage.py collectstatic --noinput")

    print("\n[5/7] Seeding project houses...")
    if os.path.exists('seed_projecthouses.py'):
        run(f"{sys.executable} seed_projecthouses.py")

    print("\n[6/7] Creating admin user...")
    import django
    django.setup()
    from apps.core.models import User
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'schonesheimbuilders@gmail.com', 'Admin123!')
        print("  Admin created: admin / Admin123!")
    else:
        print("  Admin exists.")

    print("\n[7/7] Checking .env...")
    if os.path.exists(".env"):
        with open(".env") as f:
            c = f.read()
        changed = False
        if "yourdomain.com" in c:
            c = c.replace("yourdomain.com", "schones-heim-builders.co.ke")
            c = c.replace("www.yourdomain.com", "www.schones-heim-builders.co.ke")
            changed = True
        if changed:
            with open(".env", "w") as f:
                f.write(c)
            print("  Fixed .env domain")
        else:
            print("  .env OK")

    if os.path.exists("passenger_wsgi.py"):
        os.utime("passenger_wsgi.py", None)

    print("\n" + "=" * 60)
    print("  DONE! Restart app in cPanel.")
    print("  Login: admin / Admin123!")
    print("=" * 60)

if __name__ == '__main__':
    main()
