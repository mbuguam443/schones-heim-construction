from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.views.generic.base import View
from django.contrib import messages
from apps.projects.models import Project
from .models import Equipment, EquipmentUsageLog, MaintenanceRecord
from .forms import EquipmentForm, UsageLogForm, MaintenanceRecordForm


class EquipmentListView(LoginRequiredMixin, ListView):
    model = Equipment
    template_name = 'equipment/equipment_list.html'
    context_object_name = 'equipment_list'

    def get_queryset(self):
        qs = super().get_queryset()
        cancelled = self.request.GET.get('cancelled')
        if cancelled != '1':
            qs = qs.filter(is_active=True)
        project_id = self.request.session.get('active_project_id')
        client_id = self.request.session.get('active_client_id')
        if project_id:
            equip_ids = EquipmentUsageLog.objects.filter(project_id=project_id).values_list('equipment_id', flat=True).distinct()
            qs = qs.filter(pk__in=list(equip_ids))
        elif client_id:
            proj_ids = list(Project.objects.filter(client_id=client_id).values_list('pk', flat=True))
            equip_ids = EquipmentUsageLog.objects.filter(project_id__in=proj_ids).values_list('equipment_id', flat=True).distinct()
            qs = qs.filter(pk__in=list(equip_ids))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['show_cancelled'] = self.request.GET.get('cancelled') == '1'
        ctx['cancelled_count'] = Equipment.objects.filter(is_active=False).count()
        return ctx


class EquipmentCreateView(LoginRequiredMixin, CreateView):
    model = Equipment
    form_class = EquipmentForm
    template_name = 'equipment/equipment_form.html'
    success_url = reverse_lazy('equipment_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['show_project_context_bar'] = False
        return ctx


class EquipmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Equipment
    form_class = EquipmentForm
    template_name = 'equipment/equipment_form.html'
    success_url = reverse_lazy('equipment_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['show_project_context_bar'] = False
        return ctx


class EquipmentCancelView(LoginRequiredMixin, View):
    def get(self, request, pk):
        equip = get_object_or_404(Equipment, pk=pk)
        equip.cancel()
        messages.success(request, f'Equipment "{equip.name}" cancelled.')
        return redirect('equipment_list')


class EquipmentRestoreView(LoginRequiredMixin, View):
    def get(self, request, pk):
        equip = get_object_or_404(Equipment, pk=pk)
        equip.restore()
        messages.success(request, f'Equipment "{equip.name}" restored.')
        return redirect('equipment_list')


class EquipmentDetailView(LoginRequiredMixin, DetailView):
    model = Equipment
    template_name = 'equipment/equipment_detail.html'
    context_object_name = 'equipment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        logs = self.object.usage_logs.all()
        project_id = self.request.session.get('active_project_id')
        client_id = self.request.session.get('active_client_id')
        if project_id:
            logs = logs.filter(project_id=project_id)
        elif client_id:
            proj_ids = list(Project.objects.filter(client_id=client_id).values_list('pk', flat=True))
            logs = logs.filter(project_id__in=proj_ids)
        context['usage_logs'] = logs
        context['maintenance_records'] = self.object.maintenance_records.all()
        return context


class UsageLogCreateView(LoginRequiredMixin, CreateView):
    model = EquipmentUsageLog
    form_class = UsageLogForm
    template_name = 'equipment/equipment_form.html'

    def get_initial(self):
        initial = super().get_initial()
        initial['equipment'] = self.kwargs.get('pk')
        from apps.core.mixins import get_active_project
        proj = get_active_project(self.request)
        if proj:
            initial['project'] = proj
        return initial

    def get_success_url(self):
        return reverse_lazy('equipment_detail', kwargs={'pk': self.kwargs.get('pk')})


class MaintenanceCreateView(LoginRequiredMixin, CreateView):
    model = MaintenanceRecord
    form_class = MaintenanceRecordForm
    template_name = 'equipment/equipment_form.html'

    def get_initial(self):
        initial = super().get_initial()
        initial['equipment'] = self.kwargs.get('pk')
        return initial

    def get_success_url(self):
        return reverse_lazy('equipment_detail', kwargs={'pk': self.kwargs.get('pk')})
