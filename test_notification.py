import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
os.environ['DB_ENGINE'] = 'django.db.backends.sqlite3'

import django
django.setup()

from apps.core.models import Notification, User

client = User.objects.filter(username='client5').first()
if client:
    n = Notification.objects.create(
        recipient=client,
        title='Test Inquiry',
        message='I have a question about my project budget.',
        link='/inquiries/',
    )
    print(f'Created notification #{n.pk} for {client.get_full_name()}')
    count = Notification.objects.filter(recipient=client, is_read=False).count()
    print(f'Unread count: {count}')
else:
    print('client5 not found')
