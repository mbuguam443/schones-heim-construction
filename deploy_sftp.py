#!/usr/bin/env python
"""Deploy project to cPanel via SFTP"""
import os
import sys
import paramiko

# SFTP Config
SFTP_HOST = "102.203.116.2"
SFTP_PORT = 1624
SFTP_USER = "wlsihszp"
SFTP_PASS = "9;fIpPJJvu99!2"
REMOTE_BASE = "/home/wlsihszp"

# Local project root
LOCAL_ROOT = os.path.dirname(os.path.abspath(__file__))

# Folders to upload
UPLOAD_DIRS = [
    "apps", "config", "templates", "static", "media",
]
UPLOAD_FILES = [
    "manage.py", "passenger_wsgi.py", "requirements.txt",
    "seed_data.py", "update.py", ".env.production",
]

# Skip patterns
SKIP_PATTERNS = ["__pycache__", ".pyc", ".git", "construction_db", "db.sqlite3"]

def should_skip(path):
    for skip in SKIP_PATTERNS:
        if skip in path:
            return True
    return False

def upload_dir(sftp, local_dir, remote_dir):
    """Recursively upload a directory"""
    try:
        sftp.mkdir(remote_dir)
    except:
        pass
    
    for item in os.listdir(local_dir):
        local_path = os.path.join(local_dir, item)
        remote_path = f"{remote_dir}/{item}"
        
        if should_skip(local_path):
            continue
        
        if os.path.isdir(local_path):
            upload_dir(sftp, local_path, remote_path)
        else:
            print(f"  Uploading: {remote_path}")
            try:
                sftp.put(local_path, remote_path)
            except Exception as e:
                print(f"    ERROR: {e}")

def main():
    print("\n" + "="*60)
    print("  SCHONES HEIM BUILDERS - SFTP Deployment")
    print("="*60)
    
    # Connect
    print(f"\nConnecting to {SFTP_HOST}:{SFTP_PORT}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SFTP_HOST, port=SFTP_PORT, username=SFTP_USER, password=SFTP_PASS)
    sftp = ssh.open_sftp()
    print("Connected!")
    
    # Create remote directories
    remote_home = f"{REMOTE_BASE}/public_html"
    print(f"\nDeploying to: {remote_home}")
    
    try:
        sftp.mkdir(remote_home)
    except:
        pass
    
    # Upload directories
    for dirname in UPLOAD_DIRS:
        local_path = os.path.join(LOCAL_ROOT, dirname)
        if os.path.exists(local_path):
            print(f"\nUploading directory: {dirname}/")
            upload_dir(sftp, local_path, f"{remote_home}/{dirname}")
    
    # Upload individual files
    print(f"\nUploading files:")
    for filename in UPLOAD_FILES:
        local_path = os.path.join(LOCAL_ROOT, filename)
        if os.path.exists(local_path):
            remote_path = f"{remote_home}/{filename}"
            print(f"  Uploading: {remote_path}")
            try:
                sftp.put(local_path, remote_path)
            except Exception as e:
                print(f"    ERROR: {e}")
    
    sftp.close()
    ssh.close()
    
    print("\n" + "="*60)
    print("  DEPLOYMENT COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. SSH into server and run:")
    print(f"   cd {remote_home}")
    print("   pip install -r requirements.txt")
    print("   python manage.py migrate")
    print("   python manage.py collectstatic --noinput")
    print("   python seed_data.py")
    print("2. Restart app in cPanel Python Setup")
    print("="*60)

if __name__ == '__main__':
    main()
