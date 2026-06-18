from django.urls import path
from . import views

app_name = 'quotations'

urlpatterns = [
    path('', views.QuotationListView.as_view(), name='list'),
    path('create/', views.QuotationCreateView.as_view(), name='create'),
    path('<int:pk>/', views.QuotationDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', views.QuotationUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.QuotationDeleteView.as_view(), name='delete'),
    path('<int:pk>/pdf/', views.quotation_pdf, name='pdf'),
    path('<int:pk>/convert-to-invoice/', views.convert_to_invoice, name='convert_to_invoice'),
    path('<int:pk>/send-email/', views.send_quotation_email, name='send_email'),
    path('<int:pk>/document/', views.quotation_document, name='document'),
    path('tiling/', views.TilingQuotationView.as_view(), name='tiling'),
]
