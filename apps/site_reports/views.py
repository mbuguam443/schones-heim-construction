import io
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, View
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from apps.core.mixins import filter_by_active_project
from .models import DailySiteReport, SiteReportPhoto
from .forms import DailySiteReportForm, SiteReportPhotoForm


class ReportListView(LoginRequiredMixin, ListView):
    model = DailySiteReport
    template_name = 'site_reports/report_list.html'
    context_object_name = 'reports'

    def get_queryset(self):
        qs = super().get_queryset()
        qs = filter_by_active_project(self.request, qs)
        project = self.request.GET.get('project')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        if project:
            qs = qs.filter(project_id=project)
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)
        return qs.select_related('project', 'submitted_by')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['projects'] = DailySiteReport.objects.values_list('project_id', 'project__name').distinct()
        return context


class ReportCreateView(LoginRequiredMixin, CreateView):
    model = DailySiteReport
    form_class = DailySiteReportForm
    template_name = 'site_reports/report_form.html'
    success_url = reverse_lazy('report_list')

    def get_initial(self):
        initial = super().get_initial()
        from apps.core.mixins import get_active_project
        proj = get_active_project(self.request)
        if proj:
            initial['project'] = proj
        return initial

    def form_valid(self, form):
        form.instance.submitted_by = self.request.user
        return super().form_valid(form)


class ReportUpdateView(LoginRequiredMixin, UpdateView):
    model = DailySiteReport
    form_class = DailySiteReportForm
    template_name = 'site_reports/report_form.html'
    success_url = reverse_lazy('report_list')


class ReportDeleteView(LoginRequiredMixin, DeleteView):
    model = DailySiteReport
    template_name = 'site_reports/report_confirm_delete.html'
    success_url = reverse_lazy('report_list')


class ReportDetailView(LoginRequiredMixin, DetailView):
    model = DailySiteReport
    template_name = 'site_reports/report_detail.html'
    context_object_name = 'report'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['photo_form'] = SiteReportPhotoForm()
        context['photos'] = self.object.photos.all()
        return context


class ReportExportPDFView(LoginRequiredMixin, View):
    def get(self, request, pk):
        report = get_object_or_404(DailySiteReport.objects.select_related('project', 'submitted_by'), pk=pk)
        photos = report.photos.all()
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph(f'Site Report - {report.project.name}', styles['Title']))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f'Date: {report.date}', styles['Normal']))
        elements.append(Paragraph(f'Weather: {report.weather}', styles['Normal']))
        elements.append(Paragraph(f'Workers Present: {report.workers_present}', styles['Normal']))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph('Tasks Completed:', styles['Heading2']))
        elements.append(Paragraph(report.tasks_completed or 'N/A', styles['Normal']))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph('Materials Used:', styles['Heading2']))
        elements.append(Paragraph(report.materials_used or 'N/A', styles['Normal']))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph('Challenges:', styles['Heading2']))
        elements.append(Paragraph(report.challenges or 'None', styles['Normal']))

        doc.build(elements)
        buffer.seek(0)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="site_report_{report.pk}_{report.date}.pdf"'
        response.write(buffer.getvalue())
        return response
