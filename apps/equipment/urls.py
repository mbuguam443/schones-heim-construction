from django.urls import path
from . import views

app_name = 'equipment'

urlpatterns = [
    path('', views.EquipmentListView.as_view(), name='equipment_list'),
    path('create/', views.EquipmentCreateView.as_view(), name='equipment_create'),
    path('<int:pk>/', views.EquipmentDetailView.as_view(), name='equipment_detail'),
    path('<int:pk>/update/', views.EquipmentUpdateView.as_view(), name='equipment_update'),
    path('<int:pk>/cancel/', views.EquipmentCancelView.as_view(), name='equipment_cancel'),
    path('<int:pk>/restore/', views.EquipmentRestoreView.as_view(), name='equipment_restore'),
    path('<int:pk>/usage/add/', views.UsageLogCreateView.as_view(), name='usage_log_add'),
    path('<int:pk>/maintenance/add/', views.MaintenanceCreateView.as_view(), name='maintenance_add'),
]
