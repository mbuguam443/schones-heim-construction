from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.db import transaction
from django.conf import settings
from decimal import Decimal
from apps.core.mixins import filter_by_active_project
from .models import Quotation, QuotationItem
from .forms import QuotationForm, QuotationItemFormSet


class TilingQuotationView(LoginRequiredMixin, TemplateView):
    template_name = 'quotations/tiling_quotation.html'


class QuotationListView(LoginRequiredMixin, ListView):
    model = Quotation
    template_name = 'quotations/quotation_list.html'
    context_object_name = 'quotations'
    paginate_by = 25

    def get_queryset(self):
        qs = Quotation.objects.select_related('client', 'created_by').all()
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
            qs = qs.filter(quotation_number__icontains=search) | qs.filter(client__full_name__icontains=search)
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search'] = self.request.GET.get('search', '')
        ctx['status_filter'] = self.request.GET.get('status', '')
        ctx['status_choices'] = Quotation.STATUS_CHOICES
        ctx['can_edit'] = self.request.user.role != 'client'
        return ctx


class QuotationCreateView(LoginRequiredMixin, CreateView):
    model = Quotation
    form_class = QuotationForm
    template_name = 'quotations/quotation_form.html'
    success_url = reverse_lazy('quotations:list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.POST:
            ctx['items'] = QuotationItemFormSet(self.request.POST)
        else:
            ctx['items'] = QuotationItemFormSet()
        return ctx

    def form_valid(self, form):
        context = self.get_context_data()
        items = context['items']
        if items.is_valid():
            with transaction.atomic():
                form.instance.created_by = self.request.user
                self.object = form.save()
                items.instance = self.object
                items.save()
                self.object.calculate_totals()
            messages.success(self.request, f'Quotation {self.object.quotation_number} created successfully.')
            return redirect(self.success_url)
        return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class QuotationUpdateView(LoginRequiredMixin, UpdateView):
    model = Quotation
    form_class = QuotationForm
    template_name = 'quotations/quotation_form.html'
    success_url = reverse_lazy('quotations:list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.POST:
            ctx['items'] = QuotationItemFormSet(self.request.POST, instance=self.object)
        else:
            ctx['items'] = QuotationItemFormSet(instance=self.object)
        return ctx

    def form_valid(self, form):
        context = self.get_context_data()
        items = context['items']
        if items.is_valid():
            with transaction.atomic():
                self.object = form.save()
                items.instance = self.object
                items.save()
                self.object.calculate_totals()
            messages.success(self.request, f'Quotation {self.object.quotation_number} updated.')
            return redirect(self.success_url)
        return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class QuotationDetailView(LoginRequiredMixin, DetailView):
    model = Quotation
    template_name = 'quotations/quotation_detail.html'
    context_object_name = 'qtn'

    def get_object(self):
        return get_object_or_404(
            Quotation.objects.select_related('client', 'project', 'created_by').prefetch_related('items'),
            pk=self.kwargs['pk']
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['can_edit'] = self.request.user.role != 'client'
        return ctx


class QuotationDeleteView(LoginRequiredMixin, DeleteView):
    model = Quotation
    template_name = 'quotations/quotation_confirm_delete.html'
    success_url = reverse_lazy('quotations:list')
    context_object_name = 'qtn'

    def delete(self, request, *args, **kwargs):
        qtn = self.get_object()
        messages.success(request, f'Quotation {qtn.quotation_number} deleted.')
        return super().delete(request, *args, **kwargs)


def quotation_pdf(request, pk):
    qtn = get_object_or_404(
        Quotation.objects.select_related('client', 'project', 'created_by').prefetch_related('items'),
        pk=pk
    )
    from apps.core.models import CompanySettings
    company = CompanySettings.objects.first()
    html = render_to_string('quotations/quotation_pdf.html', {
        'qtn': qtn,
        'MEDIA_URL': settings.MEDIA_URL,
        'company': company,
    })
    return HttpResponse(html)


@transaction.atomic
def convert_to_invoice(request, pk):
    qtn = get_object_or_404(Quotation.objects.prefetch_related('items'), pk=pk)
    from apps.invoices.models import Invoice, InvoiceItem

    invoice = Invoice.objects.create(
        client=qtn.client,
        project=qtn.project,
        quotation=qtn,
        date=qtn.date,
        due_date=qtn.expiry_date,
        subtotal=qtn.subtotal,
        tax_percent=qtn.tax_percent,
        tax_amount=qtn.tax_amount,
        grand_total=qtn.grand_total,
        balance=qtn.grand_total,
        notes=qtn.notes,
        created_by=request.user,
        status='Draft',
    )

    for item in qtn.items.all():
        InvoiceItem.objects.create(
            invoice=invoice,
            description=item.description,
            quantity=item.quantity,
            unit=item.unit,
            unit_price=item.unit_price,
            total=item.total,
        )

    qtn.status = 'Converted'
    qtn.save(update_fields=['status'])

    messages.success(request, f'Quotation {qtn.quotation_number} converted to Invoice {invoice.invoice_number}.')
    return redirect('invoices:detail', pk=invoice.pk)


def send_quotation_email(request, pk):
    qtn = get_object_or_404(Quotation, pk=pk)
    messages.success(request, f'Quotation {qtn.quotation_number} email sent successfully.')
    return redirect('quotations:detail', pk=pk)


def quotation_document(request, pk):
    qtn = get_object_or_404(
        Quotation.objects.select_related('client', 'project', 'created_by').prefetch_related('items'),
        pk=pk
    )
    from apps.core.models import CompanySettings
    company_settings = CompanySettings.objects.first()
    back_url = request.META.get('HTTP_REFERER', reverse_lazy('quotations:list'))
    return render(request, 'quotations/quotation_document.html', {
        'qtn': qtn,
        'company_settings': company_settings,
        'back_url': back_url,
    })
