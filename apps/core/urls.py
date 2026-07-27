from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    # SEO
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap_xml'),
    # Public pages
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('projects/', views.projects_view, name='projects'),
    path('services/', views.services_view, name='services'),
    path('contact/', views.contact_view, name='contact'),
    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('notifications/', views.notifications_list, name='notifications'),
    path('notifications/count/', views.notification_count, name='notification_count'),
    path(
        'notifications/<int:pk>/read/',
        views.mark_notification_read,
        name='mark_notification_read',
    ),
    path('settings/', views.company_settings_view, name='settings'),
    path('set-project/', views.set_active_project, name='set_project'),
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/create/', views.UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/edit/', views.UserUpdateView.as_view(), name='user_update'),
    path('users/<int:pk>/delete/', views.UserDeleteView.as_view(), name='user_delete'),
    path('users/<int:pk>/reset-password/', views.UserPasswordResetView.as_view(), name='user_password_reset'),
    # Client Inquiries
    path('inquiries/', views.ClientInquiryListView.as_view(), name='inquiry_list'),
    path('inquiries/create/', views.ClientInquiryCreateView.as_view(), name='inquiry_create'),
    path('inquiries/<int:pk>/', views.ClientInquiryDetailView.as_view(), name='inquiry_detail'),
    path('inquiries/<int:pk>/respond/', views.respond_to_inquiry, name='inquiry_respond'),
    # Project Houses (Admin)
    path('project-houses/', views.ProjectHouseListView.as_view(), name='projecthouse_list'),
    path('project-houses/create/', views.ProjectHouseCreateView.as_view(), name='projecthouse_create'),
    path('project-houses/<int:pk>/edit/', views.ProjectHouseUpdateView.as_view(), name='projecthouse_update'),
    path('project-houses/<int:pk>/delete/', views.ProjectHouseDeleteView.as_view(), name='projecthouse_delete'),
    # Contact Messages
    path('contact-messages/', views.ContactSubmissionListView.as_view(), name='contactsubmission_list'),
    path('contact-messages/<int:pk>/', views.ContactSubmissionDetailView.as_view(), name='contactsubmission_detail'),
    path('contact-messages/<int:pk>/update/', views.contact_submission_update, name='contactsubmission_update'),
    path('contact-messages/<int:pk>/delete/', views.contact_submission_delete, name='contactsubmission_delete'),
]
