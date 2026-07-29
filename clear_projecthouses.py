#!/usr/bin/env python
"""Clear all ProjectHouse records from the database."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
import django
django.setup()
from apps.core.models import ProjectHouse
count = ProjectHouse.objects.count()
ProjectHouse.objects.all().delete()
print(f"Cleared {count} project house records")
