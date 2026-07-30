#!/usr/bin/env python
"""Run Django migrations."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
import django
from django.core.management import execute_from_command_line
execute_from_command_line(['manage.py', 'migrate'])
print("Migrations complete")
