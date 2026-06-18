from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.ProjectListView.as_view(), name='project_list'),
    path('create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('<int:pk>/update/', views.ProjectUpdateView.as_view(), name='project_update'),
    path('<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project_delete'),
    path('<int:pk>/progress/', views.ProjectProgressUpdateView.as_view(), name='project_progress'),
    path('<int:pk>/assign/', views.ProjectAssignmentCreateView.as_view(), name='project_assign'),
    path('<int:pk>/photo/add/', views.ProjectPhotoCreateView.as_view(), name='project_photo_add'),
    path('<int:pk>/document/add/', views.ProjectDocumentCreateView.as_view(), name='project_document_add'),
    path('assignment/<int:pk>/delete/', views.ProjectAssignmentDeleteView.as_view(), name='assignment_delete'),
]
