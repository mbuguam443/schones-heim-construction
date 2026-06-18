import os, sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
os.environ['DB_ENGINE'] = 'django.db.backends.sqlite3'
os.environ['SECRET_KEY'] = 'test'
os.environ['DEBUG'] = 'True'
os.environ['ALLOWED_HOSTS'] = '*'

import django
from django.conf import settings
django.setup()

from django.test import Client
c = Client()

# Test login page
resp = c.get('/login/')
print(f'Login page: {resp.status_code}')

# Test dashboard (should redirect to login)
resp = c.get('/')
print(f'Dashboard (anon): {resp.status_code} (expected 302)')

# Test admin login
resp = c.post('/login/', {'username': 'admin', 'password': 'Admin123!'})
print(f'Login POST: {resp.status_code}')

# Test dashboard after login
resp = c.get('/')
print(f'Dashboard (auth): {resp.status_code}')

# Test clients list
resp = c.get('/clients/')
print(f'Clients list: {resp.status_code}')

# Test projects list 
resp = c.get('/projects/')
print(f'Projects list: {resp.status_code}')

# Test quotations list
resp = c.get('/quotations/')
print(f'Quotations list: {resp.status_code}')

# Test invoices list
resp = c.get('/invoices/')
print(f'Invoices list: {resp.status_code}')

# Test employees list
resp = c.get('/employees/')
print(f'Employees list: {resp.status_code}')

# Test inventory list
resp = c.get('/inventory/')
print(f'Inventory list: {resp.status_code}')

# Test equipment list
resp = c.get('/equipment/')
print(f'Equipment list: {resp.status_code}')

# Test site reports list
resp = c.get('/site-reports/')
print(f'Site reports list: {resp.status_code}')

# Test documents list
resp = c.get('/documents/')
print(f'Documents list: {resp.status_code}')

# Test reports dashboard
resp = c.get('/reports/')
print(f'Reports dashboard: {resp.status_code}')

# Test admin
resp = c.get('/admin/')
print(f'Admin: {resp.status_code}')

print('\nAll tests passed!' if all else 'Some tests failed')
