import os, sys, django

sys.path.insert(0, os.path.dirname(__file__))
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

# Use SQLite for validation
os.environ['DB_ENGINE'] = 'django.db.backends.sqlite3'

from django.conf import settings
settings.DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': ':memory:',
}
settings.DEBUG = True
settings.SECRET_KEY = 'test'

django.setup()

from django.core.management import call_command
call_command('makemigrations', 'core', 'clients', 'projects', 'quotations', 'invoices', 'employees', 'inventory', 'equipment', 'site_reports', 'documents', 'reports', verbosity=2)
call_command('migrate', verbosity=1, run_syncdb=True)
print('SUCCESS: All models valid, migrations applied!')
