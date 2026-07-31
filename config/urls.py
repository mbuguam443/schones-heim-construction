from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('clients/', include('apps.clients.urls')),
    path('projects/', include('apps.projects.urls')),
    path('quotations/', include('apps.quotations.urls')),
    path('invoices/', include('apps.invoices.urls')),
    path('employees/', include('apps.employees.urls')),
    path('inventory/', include('apps.inventory.urls')),
    path('equipment/', include('apps.equipment.urls')),
    path('site-reports/', include('apps.site_reports.urls')),
    path('documents/', include('apps.documents.urls')),
    path('reports/', include('apps.reports.urls')),
    path('contracts/', include('apps.contracts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    from django.views.static import serve as media_serve
    import re
    def protected_media(request, path):
        return media_serve(request, path, document_root=str(settings.MEDIA_ROOT))
    urlpatterns += [
        path('media/<path:path>', protected_media, name='media'),
    ]
