from django.urls import path
from . import views

app_name = 'contracts'

urlpatterns = [
    path('', views.ContractListView.as_view(), name='list'),
    path('create/', views.ContractCreateView.as_view(), name='create'),
    path('<int:pk>/', views.ContractDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', views.ContractUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.ContractDeleteView.as_view(), name='delete'),
    path('<int:pk>/sign/', views.contract_sign, name='sign'),
    path('<int:pk>/pdf/', views.contract_pdf, name='pdf'),
]
