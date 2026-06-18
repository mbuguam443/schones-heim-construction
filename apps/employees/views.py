import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

from apps.core.mixins import filter_by_active_project
from apps.projects.models import Project
from .models import Employee, Attendance, PerformanceNote
from .forms import EmployeeForm, AttendanceForm, PerformanceNoteForm


class EmployeeListView(LoginRequiredMixin, ListView):
    model = Employee
    template_name = 'employees/employee_list.html'
    context_object_name = 'employees'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related('user')

        # Filter by active project/client via ProjectAssignment
        project_id = self.request.session.get('active_project_id')
        client_id = self.request.session.get('active_client_id')
        if project_id:
            qs = qs.filter(user__project_assignments__project_id=project_id).distinct()
        elif client_id:
            proj_ids = list(Project.objects.filter(client_id=client_id).values_list('pk', flat=True))
            qs = qs.filter(user__project_assignments__project_id__in=proj_ids).distinct()

        query = self.request.GET.get('q')
        if query:
            qs = qs.filter(
                Q(employee_id__icontains=query) |
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(user__username__icontains=query) |
                Q(phone__icontains=query) |
                Q(position__icontains=query) |
                Q(department__icontains=query)
            )
        status = self.request.GET.get('status')
        if status == 'active':
            qs = qs.filter(is_active=True)
        elif status == 'inactive':
            qs = qs.filter(is_active=False)
        department = self.request.GET.get('department')
        if department:
            qs = qs.filter(department=department)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['departments'] = Employee.Department.choices

        # Stats should reflect the filtered employee set
        filtered = self.get_queryset()
        ctx['total_count'] = filtered.count()
        ctx['active_count'] = filtered.filter(is_active=True).count()
        return ctx


class EmployeeCreateView(LoginRequiredMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'employees/employee_form.html'
    success_url = reverse_lazy('employees:employee_list')

    def form_valid(self, form):
        resp = super().form_valid(form)
        # Auto-assign to active project if set
        project_id = self.request.session.get('active_project_id')
        if project_id:
            ProjectAssignment.objects.get_or_create(
                project_id=project_id,
                employee=self.object.user,
                defaults={'assigned_by': self.request.user}
            )
            messages.success(self.request, _(f'Employee assigned to active project.'))
        messages.success(self.request, _('Employee created successfully.'))
        return resp


class EmployeeUpdateView(LoginRequiredMixin, UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'employees/employee_form.html'
    success_url = reverse_lazy('employees:employee_list')

    def form_valid(self, form):
        messages.success(self.request, _('Employee updated successfully.'))
        return super().form_valid(form)


class EmployeeDeleteView(LoginRequiredMixin, DeleteView):
    model = Employee
    template_name = 'employees/employee_confirm_delete.html'
    success_url = reverse_lazy('employees:employee_list')

    def form_valid(self, form):
        messages.success(self.request, _('Employee deleted successfully.'))
        return super().form_valid(form)


class EmployeeDetailView(LoginRequiredMixin, DetailView):
    model = Employee
    template_name = 'employees/employee_detail.html'
    context_object_name = 'employee'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        employee = self.object
        year = self.request.GET.get('year', datetime.date.today().year)
        month = self.request.GET.get('month', datetime.date.today().month)
        try:
            year = int(year)
            month = int(month)
        except (ValueError, TypeError):
            year = datetime.date.today().year
            month = datetime.date.today().month
        ctx['selected_year'] = year
        ctx['selected_month'] = month
        ctx['attendance_records'] = Attendance.objects.filter(
            employee=employee, date__year=year, date__month=month
        ).order_by('date')
        ctx['performance_notes'] = employee.performance_notes.select_related('recorded_by').all()[:20]
        present_count = Attendance.objects.filter(employee=employee, date__year=year, date__month=month, status='present').count()
        absent_count = Attendance.objects.filter(employee=employee, date__year=year, date__month=month, status='absent').count()
        late_count = Attendance.objects.filter(employee=employee, date__year=year, date__month=month, status='late').count()
        half_count = Attendance.objects.filter(employee=employee, date__year=year, date__month=month, status='half_day').count()
        ctx['present_count'] = present_count
        ctx['absent_count'] = absent_count
        ctx['late_count'] = late_count
        ctx['half_count'] = half_count
        return ctx


class AttendanceListView(LoginRequiredMixin, ListView):
    model = Attendance
    template_name = 'employees/attendance_list.html'
    context_object_name = 'attendances'
    paginate_by = 31

    def get_queryset(self):
        qs = super().get_queryset().select_related('employee__user')
        year = self.request.GET.get('year', datetime.date.today().year)
        month = self.request.GET.get('month', datetime.date.today().month)
        try:
            year = int(year)
            month = int(month)
        except (ValueError, TypeError):
            year = datetime.date.today().year
            month = datetime.date.today().month
        self.current_year = year
        self.current_month = month
        qs = qs.filter(date__year=year, date__month=month)
        employee_id = self.request.GET.get('employee')
        if employee_id:
            qs = qs.filter(employee_id=employee_id)
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['selected_year'] = getattr(self, 'current_year', datetime.date.today().year)
        ctx['selected_month'] = getattr(self, 'current_month', datetime.date.today().month)
        ctx['employees'] = Employee.objects.filter(is_active=True).select_related('user')
        present = Attendance.objects.filter(
            date__year=ctx['selected_year'], date__month=ctx['selected_month'], status='present'
        ).count()
        absent = Attendance.objects.filter(
            date__year=ctx['selected_year'], date__month=ctx['selected_month'], status='absent'
        ).count()
        late = Attendance.objects.filter(
            date__year=ctx['selected_year'], date__month=ctx['selected_month'], status='late'
        ).count()
        half = Attendance.objects.filter(
            date__year=ctx['selected_year'], date__month=ctx['selected_month'], status='half_day'
        ).count()
        ctx['present_count'] = present
        ctx['absent_count'] = absent
        ctx['late_count'] = late
        ctx['half_count'] = half
        return ctx


class MarkAttendanceView(LoginRequiredMixin, FormView):
    template_name = 'employees/attendance_form.html'
    form_class = AttendanceForm
    success_url = reverse_lazy('employees:attendance_list')

    def form_valid(self, form):
        attendance = form.save(commit=False)
        attendance.recorded_by = self.request.user
        attendance.save()
        messages.success(self.request, _('Attendance recorded for {employee}.').format(employee=attendance.employee))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = _('Mark Attendance')
        ctx['is_update'] = False
        return ctx


class AttendanceUpdateView(LoginRequiredMixin, UpdateView):
    model = Attendance
    form_class = AttendanceForm
    template_name = 'employees/attendance_form.html'
    success_url = reverse_lazy('employees:attendance_list')

    def form_valid(self, form):
        messages.success(self.request, _('Attendance updated successfully.'))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = _('Edit Attendance')
        ctx['is_update'] = True
        return ctx


class PerformanceCreateView(LoginRequiredMixin, CreateView):
    model = PerformanceNote
    form_class = PerformanceNoteForm
    template_name = 'employees/employee_form.html'

    def get_initial(self):
        initial = super().get_initial()
        employee_id = self.kwargs.get('pk')
        if employee_id:
            initial['employee'] = employee_id
        return initial

    def form_valid(self, form):
        note = form.save(commit=False)
        note.recorded_by = self.request.user
        note.save()
        messages.success(self.request, _('Performance note added.'))
        return redirect('employees:employee_detail', pk=note.employee_id)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = _('Add Performance Note')
        ctx['is_performance'] = True
        return ctx
