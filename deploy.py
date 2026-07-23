import os
import zipfile
import shutil

# Paths
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(PROJECT_ROOT, '..', 'schones-heim-deployment.zip')

# Files/folders to exclude
EXCLUDE = {
    '__pycache__', '.git', '.venv', 'venv', 'env',
    '*.pyc', '*.pyo', '.env', 'construction_db',
    'db.sqlite3', '*.sqlite3', 'test_notification.py',
    'logins.txt', 'node_modules', '.idea', '.vscode',
    'schones-heim-deployment.zip', 'deploy.py'
}

def should_exclude(name):
    for pattern in EXCLUDE:
        if pattern.startswith('*'):
            if name.endswith(pattern[1:]):
                return True
        elif name == pattern:
            return True
    return False

print("Creating deployment package...")
with zipfile.ZipFile(OUTPUT_FILE, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Remove excluded dirs
        dirs[:] = [d for d in dirs if not should_exclude(d)]
        
        for file in files:
            if should_exclude(file):
                continue
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, PROJECT_ROOT)
            zipf.write(file_path, arcname)
            print(f"  Added: {arcname}")

print(f"\nDeployment package created: {OUTPUT_FILE}")
print(f"Size: {os.path.getsize(OUTPUT_FILE) / 1024 / 1024:.2f} MB")
