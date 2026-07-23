#!/usr/bin/env python
"""
SCHONES HEIM BUILDERS - Update Script
Pulls latest changes from GitHub and updates the live server.
Run this on your cPanel terminal after pushing to GitHub.
"""

import subprocess
import sys
import os
import shutil
from datetime import datetime

# Configuration
GITHUB_REPO = "https://github.com/mbuguam443/schones-heim-construction.git"
BACKUP_DIR = f"backups_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def run_cmd(cmd, desc=""):
    """Run a command and print output"""
    print(f"\n{'='*50}")
    print(f">> {desc}")
    print(f"{'='*50}")
    result = subprocess.run(cmd, shell=True, capture_output=False, text=True)
    if result.returncode != 0:
        print(f"ERROR: {desc} failed!")
        return False
    return True

def backup():
    """Backup current database and media"""
    print("\n[1/6] Creating backup...")
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # Backup database
    from decouple import config
    db_name = config('DB_NAME')
    db_user = config('DB_USER')
    db_pass = config('DB_PASSWORD')
    
    backup_file = f"{BACKUP_DIR}/database_backup.sql"
    cmd = f'mysqldump -u {db_user} -p"{db_pass}" {db_name} > {backup_file}'
    run_cmd(cmd, "Backing up database")
    
    # Backup media
    if os.path.exists('media'):
        shutil.copytree('media', f'{BACKUP_DIR}/media_backup')
        print(f"  Media backed up to {BACKUP_DIR}/media_backup")
    
    print(f"  Backup saved to: {BACKUP_DIR}/")

def pull_changes():
    """Pull latest changes from GitHub"""
    print("\n[2/6] Pulling from GitHub...")
    run_cmd("git fetch origin", "Fetching latest changes")
    run_cmd("git reset --hard origin/main", "Resetting to latest commit")
    run_cmd("git pull origin main", "Pulling latest code")

def install_requirements():
    """Install updated requirements"""
    print("\n[3/6] Installing requirements...")
    run_cmd(f"{sys.executable} -m pip install -r requirements.txt --upgrade", 
            "Installing Python packages")

def run_migrations():
    """Run database migrations"""
    print("\n[4/6] Running migrations...")
    run_cmd(f"{sys.executable} manage.py migrate", "Applying database migrations")

def collect_static():
    """Collect static files"""
    print("\n[5/6] Collecting static files...")
    run_cmd(f"{sys.executable} manage.py collectstatic --noinput", "Collecting static files")

def restart_app():
    """Restart the Python application"""
    print("\n[6/6] Restarting application...")
    # Touch passenger_wsgi.py to trigger restart
    if os.path.exists('passenger_wsgi.py'):
        os.utime('passenger_wsgi.py', None)
        print("  Application restarted (passenger_wsgi.py touched)")
    else:
        print("  WARNING: passenger_wsgi.py not found - manually restart in cPanel")

def main():
    print("\n" + "="*60)
    print("  SCHONES HEIM BUILDERS - System Update")
    print("="*60)
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Repo: {GITHUB_REPO}")
    print("="*60)
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("\nERROR: .env file not found!")
        print("Please create .env with your production settings.")
        return
    
    # Run update steps
    backup()
    pull_changes()
    install_requirements()
    run_migrations()
    collect_static()
    restart_app()
    
    print("\n" + "="*60)
    print("  UPDATE COMPLETE!")
    print("="*60)
    print(f"  Backup location: {BACKUP_DIR}/")
    print("  Your site is now updated with the latest changes.")
    print("="*60)

if __name__ == '__main__':
    main()
