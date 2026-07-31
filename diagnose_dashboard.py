#!/usr/bin/env python
"""Print the real error behind the dashboard 500. Run: python diagnose_dashboard.py"""
import os, sys, traceback
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
os.environ.setdefault('DEBUG', 'True')
import django
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()
username = sys.argv[1] if len(sys.argv) > 1 else 'admin'
user = User.objects.filter(username=username).first()
if not user:
    print(f"User '{username}' not found.")
    sys.exit(1)

c = Client()
c.force_login(user)
try:
    r = c.get('/dashboard/')
    print("STATUS:", r.status_code)
    if r.status_code >= 400:
        print("BODY (first 3000 chars):")
        print(r.content.decode('utf-8', 'replace')[:3000])
    else:
        print("Dashboard rendered OK.")
except Exception:
    traceback.print_exc()
