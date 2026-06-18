from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_dashboard, name='report_dashboard'),
    path('financial/', views.financial_report, name='financial_report'),
    path('projects/', views.project_report, name='project_report'),
    path('inventory/', views.inventory_report, name='inventory_report'),
    path('employees/', views.employee_report, name='employee_report'),
    path('export/pdf/<str:report_type>/', views.export_pdf, name='export_pdf'),
    path('export/excel/<str:report_type>/', views.export_excel, name='export_excel'),
]
