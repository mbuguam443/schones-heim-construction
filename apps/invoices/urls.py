from django.urls import path
from . import views

app_name = 'invoices'

urlpatterns = [
    path('', views.InvoiceListView.as_view(), name='list'),
    path('create/', views.InvoiceCreateView.as_view(), name='create'),
    path('<int:pk>/', views.InvoiceDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', views.InvoiceUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.InvoiceDeleteView.as_view(), name='delete'),
    path('<int:pk>/pdf/', views.invoice_pdf, name='pdf'),
    path('<int:pk>/record-payment/', views.record_payment, name='record_payment'),
]
