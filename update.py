#!/usr/bin/env python
"""
SCHONES HEIM BUILDERS - Server Update Script
Downloads latest code from GitHub and updates the server.
Run: python update.py
"""
import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil
from datetime import datetime

GITHUB_ZIP = "https://github.com/mbuguam443/schones-heim-construction/archive/refs/heads/main.zip"
BACKUP_DIR = f"backups_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
TEMP_DIR = "_update_temp"

def run(cmd):
    print(f"\n>> {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result.returncode == 0

def main():
    print("\n" + "=" * 60)
    print("  SCHONES HEIM BUILDERS - Server Update")
    print("=" * 60)
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Step 1: Backup
    print("\n[1/6] Creating backup...")
    os.makedirs(BACKUP_DIR, exist_ok=True)
    for d in ["apps", "config", "templates", "static", "media"]:
        if os.path.exists(d):
            shutil.copytree(d, f"{BACKUP_DIR}/{d}", dirs_exist_ok=True)
    for f in ["manage.py", "passenger_wsgi.py", "requirements.txt", "seed_data.py"]:
        if os.path.exists(f):
            shutil.copy2(f, f"{BACKUP_DIR}/{f}")
    print(f"  Backup saved to {BACKUP_DIR}/")

    # Step 2: Download latest from GitHub
    print("\n[2/6] Downloading latest code from GitHub...")
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR)
    
    try:
        urllib.request.urlretrieve(GITHUB_ZIP, f"{TEMP_DIR}/main.zip")
        print("  Downloaded successfully!")
    except Exception as e:
        print(f"  ERROR downloading: {e}")
        print("  Make sure you have internet access on the server.")
        return

    # Step 3: Extract
    print("\n[3/6] Extracting files...")
    with zipfile.ZipFile(f"{TEMP_DIR}/main.zip", 'r') as z:
        z.extractall(TEMP_DIR)
    
    # Find extracted folder (schones-heim-construction-main/)
    extracted = os.path.join(TEMP_DIR, "schones-heim-construction-main")
    if not os.path.exists(extracted):
        # Try finding it
        for item in os.listdir(TEMP_DIR):
            if os.path.isdir(os.path.join(TEMP_DIR, item)):
                extracted = os.path.join(TEMP_DIR, item)
                break

    # Step 4: Copy updated files
    print("\n[4/6] Updating files...")
    KEEP_FILES = [".env", "media", "staticfiles"]
    DIRS_TO_UPDATE = ["apps", "config", "templates", "static"]
    
    for dirname in DIRS_TO_UPDATE:
        src = os.path.join(extracted, dirname)
        dst = dirname
        if os.path.exists(src):
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f"  Updated: {dirname}/")
    
    FILES_TO_UPDATE = ["manage.py", "passenger_wsgi.py", "requirements.txt", "seed_data.py", "setup.py"]
    for filename in FILES_TO_UPDATE:
        src = os.path.join(extracted, filename)
        if os.path.exists(src):
            shutil.copy2(src, filename)
            print(f"  Updated: {filename}")

    # Step 5: Install updated requirements
    print("\n[5/6] Installing updated packages...")
    run(f"{sys.executable} -m pip install -r requirements.txt -q")

    # Step 6: Run migrations
    print("\n[6/6] Running migrations...")
    run(f"{sys.executable} manage.py migrate")
    run(f"{sys.executable} manage.py collectstatic --noinput")

    # Fix .env if placeholder domain is still there
    print("\n[Fix] Checking .env for placeholder domain...")
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            content = f.read()
        if "yourdomain.com" in content:
            content = content.replace("yourdomain.com", "*")
            content = content.replace("ALLOWED_HOSTS=*\n*", "ALLOWED_HOSTS=*")
            content = content.replace("CSRF_TRUSTED_ORIGINS=https://*", "CSRF_TRUSTED_ORIGINS=*")
            with open(".env", "w") as f:
                f.write(content)
            print("  Fixed: replaced placeholder domain with *")
        else:
            print("  .env looks good.")

    # Cleanup
    shutil.rmtree(TEMP_DIR, ignore_errors=True)

    # Touch passenger_wsgi.py to restart app
    if os.path.exists("passenger_wsgi.py"):
        os.utime("passenger_wsgi.py", None)

    print("\n" + "=" * 60)
    print("  UPDATE COMPLETE!")
    print("=" * 60)
    print(f"  Backup: {BACKUP_DIR}/")
    print("  Restart your Python App in cPanel.")
    print("=" * 60)

if __name__ == "__main__":
    main()
