from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.MaterialListView.as_view(), name='material_list'),
    path('create/', views.MaterialCreateView.as_view(), name='material_create'),
    path('<int:pk>/update/', views.MaterialUpdateView.as_view(), name='material_update'),
    path('<int:pk>/cancel/', views.MaterialCancelView.as_view(), name='material_cancel'),
    path('<int:pk>/restore/', views.MaterialRestoreView.as_view(), name='material_restore'),
    path('stock-in/', views.StockInView.as_view(), name='stock_in'),
    path('stock-out/', views.StockOutView.as_view(), name='stock_out'),
    path('low-stock/', views.LowStockAlertsView.as_view(), name='low_stock'),
    path('transactions/', views.StockTransactionListView.as_view(), name='stock_transactions'),
]
