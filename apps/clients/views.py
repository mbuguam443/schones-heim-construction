import secrets
import string

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.db.models import Q
from .models import Client
from .forms import ClientForm
from apps.core.models import User


def is_admin_or_pm(user):
    return user.role in ('admin', 'project_manager')


class AdminOrPMMixin(UserPassesTestMixin):
    def test_func(self):
        return is_admin_or_pm(self.request.user)


class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'clients/client_list.html'
    context_object_name = 'clients'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q', '').strip()
        if q:
            return qs.filter(
                Q(full_name__icontains=q) |
                Q(company_name__icontains=q) |
                Q(email__icontains=q) |
                Q(phone__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search_query'] = self.request.GET.get('q', '')
        ctx['can_edit'] = is_admin_or_pm(self.request.user)
        return ctx


class ClientCreateView(LoginRequiredMixin, AdminOrPMMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('clients:client_list')

    def form_valid(self, form):
        client = form.save(commit=False)
        client.created_by = self.request.user
        user, password = self._create_portal_user(client)
        client.user = user
        client.save()
        messages.success(
            self.request,
            f'Client "{client.full_name}" created. '
            f'Portal login - Username: {user.username}, Password: {password}',
        )
        return super().form_valid(form)

    def _create_portal_user(self, client):
        email = (client.email or '').strip().lower()
        base = email.split('@')[0] if email else client.full_name.strip().replace(' ', '_').lower()
        if not base or not base.replace('_', '').isalnum():
            base = 'client'
        username, n = base, 1
        while User.objects.filter(username=username).exists():
            n += 1
            username = f'{base}_{n}'
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for _ in range(12))
        user = User.objects.create_user(username=username, password=password, email=email, first_name=client.full_name)
        user.role = User.Role.CLIENT
        user.save()
        return user, password


class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    template_name = 'clients/client_detail.html'
    context_object_name = 'client'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['projects'] = self.object.project_set.all()
        ctx['can_edit'] = is_admin_or_pm(self.request.user)
        return ctx


class ClientUpdateView(LoginRequiredMixin, AdminOrPMMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('clients:client_list')


class ClientDeleteView(LoginRequiredMixin, AdminOrPMMixin, DeleteView):
    model = Client
    template_name = 'clients/client_confirm_delete.html'
    success_url = reverse_lazy('clients:client_list')
