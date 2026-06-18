from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('', views.DocumentListView.as_view(), name='document_list'),
    path('upload/', views.DocumentCreateView.as_view(), name='document_upload'),
    path('<int:pk>/', views.DocumentUpdateView.as_view(), name='document_update'),
    path('<int:pk>/cancel/', views.DocumentCancelView.as_view(), name='document_cancel'),
    path('<int:pk>/restore/', views.DocumentRestoreView.as_view(), name='document_restore'),
    path('<int:pk>/download/', views.DocumentDownloadView.as_view(), name='document_download'),
    path('categories/', views.DocumentCategoryListView.as_view(), name='document_categories'),
]
