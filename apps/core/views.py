import json
from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST, require_http_methods

from .decorators import role_required
from .forms import CompanySettingsForm, LoginForm, UserProfileForm
from .models import ActivityLog, CompanySettings, Notification, User


def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                user.is_online = True
                user.save(update_fields=['is_online'])
                messages.success(request, _(f'Welcome back, {user.get_full_name() or user.username}!'))
                return redirect('core:dashboard')
        messages.error(request, _('Invalid username or password.'))
    else:
        form = LoginForm()

    return render(request, 'registration/login.html', {'form': form})


@login_required
def dashboard_view(request):
    user = request.user
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    is_client = user.role == User.Role.CLIENT

    if is_client:
        from django.apps import apps
        Project = apps.get_model('projects', 'Project') if apps.is_installed('apps.projects') else None
        Invoice = apps.get_model('invoices', 'Invoice') if apps.is_installed('apps.invoices') else None
        profile = getattr(user, 'client_profile', None)
        total_projects = active_projects = completed_projects = 0
        pending_invoices = 0
        if profile and Project:
            total_projects = Project.objects.filter(client=profile).count()
            active_projects = Project.objects.filter(client=profile, status__in=['Ongoing', 'On Hold']).count()
            completed_projects = Project.objects.filter(client=profile, status='Completed').count()
        if profile and Invoice:
            pending_invoices = Invoice.objects.filter(client=profile, status='Pending').count()
        activity_logs = ActivityLog.objects.none()
        context = {
            'total_projects': total_projects,
            'active_projects': active_projects,
            'completed_projects': completed_projects,
            'pending_invoices': pending_invoices,
            'monthly_revenue': 0,
            'total_employees': 0,
            'total_clients': 0,
            'activity_logs': activity_logs,
            'revenue_labels': '[]',
            'revenue_data': '[]',
            'is_client': True,
        }
        return render(request, 'core/dashboard.html', context)

    total_projects = _get_count('projects.Project', None)
    active_projects = _get_count('projects.Project', {'status__in': ['Ongoing', 'On Hold']})
    completed_projects = _get_count('projects.Project', {'status': 'Completed'})
    total_clients = User.objects.filter(role=User.Role.CLIENT).count()
    total_employees = User.objects.filter(
        role__in=[User.Role.PROJECT_MANAGER, User.Role.ACCOUNTANT, User.Role.SITE_SUPERVISOR]
    ).count()

    from django.apps import apps
    Invoice = apps.get_model('invoices', 'Invoice') if apps.is_installed('apps.invoices') else None
    pending_invoices = 0
    monthly_revenue = 0
    revenue_labels = []
    revenue_data = []

    if Invoice:
        pending_invoices = Invoice.objects.filter(status='Pending').count()

        last_6_months = []
        for i in range(5, -1, -1):
            d = now.replace(day=1) - timedelta(days=30 * i)
            last_6_months.append(d.replace(day=1))

        monthly_stats = (
            Invoice.objects.filter(status='Paid', created_at__gte=last_6_months[0])
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(total=Sum('grand_total'))
            .order_by('month')
        )

        monthly_dict = {m['month']: float(m['total']) for m in monthly_stats if m['total']}
        for m in last_6_months:
            revenue_labels.append(m.strftime('%b %Y'))
            revenue_data.append(monthly_dict.get(m, 0))

        monthly_revenue = sum(revenue_data[-2:]) if len(revenue_data) >= 2 else sum(revenue_data)

    activity_logs = ActivityLog.objects.select_related('user').all()[:15]

    context = {
        'total_projects': total_projects,
        'active_projects': active_projects,
        'completed_projects': completed_projects,
        'total_clients': total_clients,
        'pending_invoices': pending_invoices,
        'monthly_revenue': monthly_revenue,
        'total_employees': total_employees,
        'activity_logs': activity_logs,
        'revenue_labels': json.dumps(revenue_labels),
        'revenue_data': json.dumps(revenue_data),
    }
    return render(request, 'core/dashboard.html', context)


def _get_count(model_path, filters):
    from django.apps import apps
    try:
        Model = apps.get_model(model_path)
        if filters:
            return Model.objects.filter(**filters).count()
        return Model.objects.count()
    except LookupError:
        return 0


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Profile updated successfully.'))
            return redirect('core:profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'core/profile.html', {'form': form})


@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(recipient=request.user)
    return render(request, 'core/notifications.html', {'notifications': notifications})


@login_required
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.is_read = True
    notification.save(update_fields=['is_read'])
    if notification.link:
        return redirect(notification.link)
    return redirect('core:notifications')


def logout_view(request):
    logout(request)
    return redirect('core:home')

@login_required
@role_required(User.Role.ADMIN)
def company_settings_view(request):
    settings = CompanySettings.objects.first()
    if request.method == 'POST':
        form = CompanySettingsForm(request.POST, request.FILES, instance=settings)
        if form.is_valid():
            settings = form.save()
            messages.success(request, _('Company settings updated successfully.'))
            return redirect('core:settings')
    else:
        form = CompanySettingsForm(instance=settings)
    return render(request, 'core/settings.html', {'form': form, 'settings': settings})


@require_http_methods(['GET', 'POST'])
def set_active_project(request):
    """Set the active client/project in session for global project context."""
    next_url = request.GET.get('next') or request.POST.get('next') or '/'
    project_id = (request.GET.get('project_id') or
                  request.POST.get('project_id') or '').strip()
    client_id = (request.GET.get('client_id') or
                 request.POST.get('client_id') or '').strip()

    if client_id:
        request.session['active_client_id'] = int(client_id)
        if 'active_project_id' in request.session:
            del request.session['active_project_id']
    elif 'active_client_id' in request.session:
        del request.session['active_client_id']

    if project_id:
        request.session['active_project_id'] = int(project_id)
        # Also sync client from the project
        from apps.projects.models import Project
        proj = Project.objects.filter(pk=project_id).select_related('client').first()
        if proj and proj.client:
            request.session['active_client_id'] = proj.client_id
    elif 'active_project_id' in request.session:
        del request.session['active_project_id']

    return redirect(next_url)


from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.db.models import Q
from .forms import UserCreateForm, UserUpdateForm, UserPasswordResetForm
from apps.clients.models import Client


class AdminOnlyMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN


class UserListView(LoginRequiredMixin, AdminOnlyMixin, ListView):
    model = User
    template_name = 'core/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        qs = User.objects.all().order_by('-date_joined')
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(username__icontains=q) |
                Q(email__icontains=q) |
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q)
            )
        role = self.request.GET.get('role', '').strip()
        if role:
            qs = qs.filter(role=role)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search_query'] = self.request.GET.get('q', '')
        ctx['role_filter'] = self.request.GET.get('role', '')
        ctx['role_choices'] = User.Role.choices
        return ctx


class UserCreateView(LoginRequiredMixin, AdminOnlyMixin, CreateView):
    model = User
    form_class = UserCreateForm
    template_name = 'core/user_form.html'
    success_url = reverse_lazy('core:user_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Create User'
        return ctx

    def form_valid(self, form):
        messages.success(self.request, f'User "{form.instance.username}" created successfully.')
        return super().form_valid(form)


class UserUpdateView(LoginRequiredMixin, AdminOnlyMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'core/user_form.html'
    success_url = reverse_lazy('core:user_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = f'Edit User: {self.object.username}'
        ctx['editing'] = True
        return ctx

    def form_valid(self, form):
        messages.success(self.request, f'User "{form.instance.username}" updated successfully.')
        return super().form_valid(form)


class UserDeleteView(LoginRequiredMixin, AdminOnlyMixin, DeleteView):
    model = User
    template_name = 'core/user_confirm_delete.html'
    success_url = reverse_lazy('core:user_list')
    context_object_name = 'user_obj'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = f'Delete User: {self.object.username}'
        return ctx

    def form_valid(self, form):
        messages.success(self.request, f'User "{self.object.username}" deleted successfully.')
        return super().form_valid(form)


class UserPasswordResetView(LoginRequiredMixin, AdminOnlyMixin, FormView):
    form_class = UserPasswordResetForm
    template_name = 'core/user_password_reset.html'

    def get_user(self):
        return get_object_or_404(User, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['target_user'] = self.get_user()
        ctx['title'] = f'Reset Password: {ctx["target_user"].username}'
        return ctx

    def form_valid(self, form):
        user = self.get_user()
        user.set_password(form.cleaned_data['new_password'])
        user.save(update_fields=['password'])
        messages.success(self.request, f'Password reset for "{user.username}" successfully.')
        return redirect('core:user_list')


#
# Public / Landing pages
#

def home_view(request):
    from apps.projects.models import Project as AllProjects
    projects = AllProjects.objects.filter(status__in=['Ongoing', 'Completed']).order_by('-id')[:6]
    company_settings = CompanySettings.objects.first()
    stats = {
        'projects_completed': 10,
        'years_established': 8,
        'happy_clients': 15,
        'professionals': User.objects.filter(is_active=True).count() or 20,
    }
    return render(request, 'public/home.html', {
        'projects': projects,
        'stats': stats,
        'company_settings': company_settings,
    })


def about_view(request):
    company_settings = CompanySettings.objects.first()
    from apps.projects.models import Project as AllProjects
    stats = {
        'projects_completed': 10,
        'years_established': 8,
        'happy_clients': 15,
        'professionals': User.objects.filter(is_active=True).count() or 20,
    }
    return render(request, 'public/about.html', {
        'stats': stats,
        'company_settings': company_settings,
    })


def services_view(request):
    company_settings = CompanySettings.objects.first()
    return render(request, 'public/services.html', {
        'company_settings': company_settings,
    })


def contact_view(request):
    company_settings = CompanySettings.objects.first()
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')
        ActivityLog.objects.create(
            user=None,
            action=f'Contact form submission: {name} ({email}) - {subject}',
            description=f'From: {name}\nEmail: {email}\nPhone: {phone}\nSubject: {subject}\nMessage: {message}',
        )
        messages.success(request, 'Thank you for your message! We will get back to you within 24 hours.')
        return redirect('core:contact')
    return render(request, 'public/contact.html', {
        'company_settings': company_settings,
    })
