from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, TemplateView
from django.views.generic.base import View
from django.db.models import F, Q
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .models import Material, StockTransaction
from apps.core.mixins import filter_by_active_project
from .forms import MaterialForm, StockInForm, StockOutForm


class AdminOrPMMaterialMixin(UserPassesTestMixin):
    """Restrict material create/update/delete to admin, pm, site_supervisor."""
    def test_func(self):
        return self.request.user.role in ('admin', 'project_manager', 'site_supervisor')


class MaterialListView(LoginRequiredMixin, ListView):
    model = Material
    template_name = 'inventory/material_list.html'
    context_object_name = 'materials'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset()
        cancelled = self.request.GET.get('cancelled')
        if cancelled != '1':
            qs = qs.filter(is_active=True)
        query = self.request.GET.get('q')
        if query:
            qs = qs.filter(
                Q(name__icontains=query) |
                Q(supplier__icontains=query) |
                Q(category__icontains=query)
            )
        category = self.request.GET.get('category')
        if category:
            qs = qs.filter(category=category)
        low = self.request.GET.get('low')
        if low == '1':
            qs = qs.filter(quantity__lte=F('reorder_level'))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = Material.Category.choices
        ctx['low_stock_count'] = Material.objects.filter(is_active=True, quantity__lte=F('reorder_level')).count()
        ctx['show_cancelled'] = self.request.GET.get('cancelled') == '1'
        ctx['cancelled_count'] = Material.objects.filter(is_active=False).count()
        return ctx


class MaterialCreateView(LoginRequiredMixin, CreateView):
    model = Material
    form_class = MaterialForm
    template_name = 'inventory/material_form.html'
    success_url = reverse_lazy('inventory:material_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['show_project_context_bar'] = False
        return ctx

    def form_valid(self, form):
        messages.success(self.request, _('Material added successfully.'))
        return super().form_valid(form)


class MaterialUpdateView(LoginRequiredMixin, AdminOrPMMaterialMixin, UpdateView):
    model = Material
    form_class = MaterialForm
    template_name = 'inventory/material_form.html'
    success_url = reverse_lazy('inventory:material_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['show_project_context_bar'] = False
        return ctx

    def form_valid(self, form):
        messages.success(self.request, _('Material updated successfully.'))
        return super().form_valid(form)


class MaterialCancelView(LoginRequiredMixin, View):
    def post(self, request, pk):
        material = get_object_or_404(Material, pk=pk)
        material.cancel()
        messages.success(request, _('Material "{name}" cancelled.').format(name=material.name))
        return redirect('inventory:material_list')

    def get(self, request, pk):
        material = get_object_or_404(Material, pk=pk)
        material.cancel()
        messages.success(request, _('Material "{name}" cancelled.').format(name=material.name))
        return redirect('inventory:material_list')


class MaterialRestoreView(LoginRequiredMixin, View):
    def post(self, request, pk):
        material = get_object_or_404(Material, pk=pk)
        material.restore()
        messages.success(request, _('Material "{name}" restored.').format(name=material.name))
        return redirect('inventory:material_list')

    def get(self, request, pk):
        material = get_object_or_404(Material, pk=pk)
        material.restore()
        messages.success(request, _('Material "{name}" restored.').format(name=material.name))
        return redirect('inventory:material_list')


class StockInView(LoginRequiredMixin, CreateView):
    model = StockTransaction
    form_class = StockInForm
    template_name = 'inventory/stock_form.html'
    success_url = reverse_lazy('inventory:material_list')

    def get_initial(self):
        initial = super().get_initial()
        from apps.core.mixins import get_active_project
        proj = get_active_project(self.request)
        if proj:
            initial['project'] = proj
        return initial

    def form_valid(self, form):
        transaction = form.save(commit=False)
        transaction.transaction_type = StockTransaction.TransactionType.IN
        transaction.done_by = self.request.user
        transaction.save()
        material = transaction.material
        material.quantity += transaction.quantity
        material.save()
        messages.success(
            self.request,
            _('Stock in: {qty} {unit} of {material} added.').format(
                qty=transaction.quantity,
                unit=material.get_unit_display(),
                material=material.name,
            ),
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = _('Stock In')
        ctx['transaction_type'] = 'in'
        return ctx


class StockOutView(LoginRequiredMixin, CreateView):
    model = StockTransaction
    form_class = StockOutForm
    template_name = 'inventory/stock_form.html'
    success_url = reverse_lazy('inventory:material_list')

    def get_initial(self):
        initial = super().get_initial()
        from apps.core.mixins import get_active_project
        proj = get_active_project(self.request)
        if proj:
            initial['project'] = proj
        return initial

    def form_valid(self, form):
        transaction = form.save(commit=False)
        transaction.transaction_type = StockTransaction.TransactionType.OUT
        transaction.done_by = self.request.user
        material = transaction.material
        if transaction.quantity > material.quantity:
            messages.error(
                self.request,
                _('Insufficient stock! Available: {available} {unit}.').format(
                    available=material.quantity,
                    unit=material.get_unit_display(),
                ),
            )
            return self.form_invalid(form)
        transaction.save()
        material.quantity -= transaction.quantity
        material.save()
        messages.success(
            self.request,
            _('Stock out: {qty} {unit} of {material} removed.').format(
                qty=transaction.quantity,
                unit=material.get_unit_display(),
                material=material.name,
            ),
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = _('Stock Out')
        ctx['transaction_type'] = 'out'
        return ctx


class LowStockAlertsView(LoginRequiredMixin, TemplateView):
    template_name = 'inventory/low_stock.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from django.db.models import F
        ctx['low_stock_materials'] = Material.objects.filter(
            quantity__lte=F('reorder_level')
        ).order_by('quantity')
        ctx['count'] = ctx['low_stock_materials'].count()
        return ctx


class StockTransactionListView(LoginRequiredMixin, ListView):
    model = StockTransaction
    template_name = 'inventory/stock_transactions.html'
    context_object_name = 'transactions'
    paginate_by = 50

    def get_queryset(self):
        qs = super().get_queryset().select_related('material', 'project', 'done_by')
        qs = filter_by_active_project(self.request, qs)
        material_id = self.request.GET.get('material')
        if material_id:
            qs = qs.filter(material_id=material_id)
        ttype = self.request.GET.get('type')
        if ttype:
            qs = qs.filter(transaction_type=ttype)
        project_id = self.request.GET.get('project')
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from apps.projects.models import Project
        ctx['projects'] = Project.objects.all().order_by('name')
        return ctx
