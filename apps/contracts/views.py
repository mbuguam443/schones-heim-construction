from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Q
from apps.core.mixins import filter_by_active_project
from .models import Contract
from .forms import ContractForm, ContractSignForm


def can_manage_contracts(user):
    return user.role in ('admin', 'project_manager', 'accountant')


class ContractListView(LoginRequiredMixin, ListView):
    model = Contract
    template_name = 'contracts/contract_list.html'
    context_object_name = 'contracts'
    paginate_by = 20

    def get_queryset(self):
        qs = Contract.objects.select_related('client', 'project', 'created_by').all()
        qs = filter_by_active_project(self.request, qs)
        user = self.request.user
        if user.role == 'client':
            profile = getattr(user, 'client_profile', None)
            if profile:
                qs = qs.filter(client=profile)
            else:
                qs = qs.none()
        search = self.request.GET.get('search', '')
        status = self.request.GET.get('status', '')
        if search:
            qs = qs.filter(Q(contract_number__icontains=search) | Q(client__full_name__icontains=search) | Q(title__icontains=search))
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search'] = self.request.GET.get('search', '')
        ctx['status_filter'] = self.request.GET.get('status', '')
        ctx['status_choices'] = Contract.STATUS_CHOICES
        ctx['can_edit'] = can_manage_contracts(self.request.user)
        return ctx


class ContractCreateView(LoginRequiredMixin, CreateView):
    model = Contract
    form_class = ContractForm
    template_name = 'contracts/contract_form.html'
    success_url = reverse_lazy('contracts:list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Contract created.')
        return super().form_valid(form)


class ContractUpdateView(LoginRequiredMixin, UpdateView):
    model = Contract
    form_class = ContractForm
    template_name = 'contracts/contract_form.html'
    success_url = reverse_lazy('contracts:list')

    def form_valid(self, form):
        messages.success(self.request, 'Contract updated.')
        return super().form_valid(form)


class ContractDetailView(LoginRequiredMixin, DetailView):
    model = Contract
    template_name = 'contracts/contract_detail.html'
    context_object_name = 'contract'

    def get_object(self):
        obj = get_object_or_404(
            Contract.objects.select_related('client', 'project', 'quotation', 'created_by'),
            pk=self.kwargs['pk']
        )
        user = self.request.user
        if user.role == 'client':
            profile = getattr(user, 'client_profile', None)
            if not profile or obj.client != profile:
                raise Http404("Contract not found")
        return obj

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx['can_edit'] = can_manage_contracts(user)
        ctx['can_client_sign'] = False
        ctx['can_owner_sign'] = can_manage_contracts(user)
        if user.role == 'client':
            profile = getattr(user, 'client_profile', None)
            ctx['can_client_sign'] = bool(profile and self.object.client == profile)
        ctx['sign_form'] = ContractSignForm()
        return ctx


class ContractDeleteView(LoginRequiredMixin, DeleteView):
    model = Contract
    template_name = 'contracts/contract_confirm_delete.html'
    success_url = reverse_lazy('contracts:list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Contract deleted.')
        return super().delete(request, *args, **kwargs)


def contract_sign_client(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    user = request.user
    profile = getattr(user, 'client_profile', None)
    is_client_owner = user.role == 'client' and profile and contract.client == profile
    is_staff = can_manage_contracts(user)
    if not (is_client_owner or is_staff):
        messages.error(request, 'You do not have permission to sign this contract.')
        return redirect('contracts:detail', pk=pk)
    if contract.client_signed:
        messages.info(request, f'{contract.contract_number} is already signed by the client.')
        return redirect('contracts:detail', pk=pk)
    if request.method == 'POST':
        form = ContractSignForm(request.POST)
        if form.is_valid():
            contract.mark_client_signed(form.cleaned_data['signature_name'])
            messages.success(request, f'{contract.contract_number} signed by the client.')
    return redirect('contracts:detail', pk=pk)


def contract_sign_owner(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    if not can_manage_contracts(request.user):
        messages.error(request, 'You do not have permission.')
        return redirect('contracts:detail', pk=pk)
    if contract.owner_signed:
        messages.info(request, f'{contract.contract_number} is already signed by the company.')
        return redirect('contracts:detail', pk=pk)
    if request.method == 'POST':
        form = ContractSignForm(request.POST)
        if form.is_valid():
            contract.mark_owner_signed(form.cleaned_data['signature_name'])
            messages.success(request, f'{contract.contract_number} signed by the company.')
    return redirect('contracts:detail', pk=pk)


def contract_pdf(request, pk):
    contract = get_object_or_404(
        Contract.objects.select_related('client', 'project', 'created_by'),
        pk=pk
    )
    from apps.core.models import CompanySettings
    company_settings = CompanySettings.objects.first()
    html = render_to_string('contracts/contract_pdf.html', {
        'contract': contract,
        'company_settings': company_settings,
        'MEDIA_URL': settings.MEDIA_URL,
    })
    return HttpResponse(html)
