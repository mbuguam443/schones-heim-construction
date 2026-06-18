from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.db import transaction
from django.conf import settings
from django.utils import timezone
from apps.core.mixins import filter_by_active_project
from .models import Invoice, InvoiceItem, Payment
from .forms import InvoiceForm, InvoiceItemFormSet, PaymentForm
from decimal import Decimal


class InvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = 'invoices/invoice_list.html'
    context_object_name = 'invoices'
    paginate_by = 25

    def get_queryset(self):
        qs = Invoice.objects.select_related('client', 'created_by').all()
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
            qs = qs.filter(invoice_number__icontains=search) | qs.filter(client__full_name__icontains=search)
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search'] = self.request.GET.get('search', '')
        ctx['status_filter'] = self.request.GET.get('status', '')
        ctx['status_choices'] = Invoice.STATUS_CHOICES
        ctx['can_edit'] = self.request.user.role in ('admin', 'accountant')
        ctx['can_delete'] = self.request.user.role in ('admin', 'accountant')
        ctx['today'] = timezone.now().date()
        return ctx


class InvoiceCreateView(LoginRequiredMixin, CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'invoices/invoice_form.html'
    success_url = reverse_lazy('invoices:list')

    def get_initial(self):
        initial = super().get_initial()
        from apps.core.mixins import get_active_project
        proj = get_active_project(self.request)
        if proj:
            initial['project'] = proj
        return initial

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.POST:
            ctx['items'] = InvoiceItemFormSet(self.request.POST)
        else:
            ctx['items'] = InvoiceItemFormSet()
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
            messages.success(self.request, f'Invoice {self.object.invoice_number} created.')
            return redirect(self.success_url)
        return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class InvoiceUpdateView(LoginRequiredMixin, UpdateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'invoices/invoice_form.html'
    success_url = reverse_lazy('invoices:list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.POST:
            ctx['items'] = InvoiceItemFormSet(self.request.POST, instance=self.object)
        else:
            ctx['items'] = InvoiceItemFormSet(instance=self.object)
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
            messages.success(self.request, f'Invoice {self.object.invoice_number} updated.')
            return redirect(self.success_url)
        return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice
    template_name = 'invoices/invoice_detail.html'
    context_object_name = 'inv'

    def get_object(self):
        obj = get_object_or_404(
            Invoice.objects.select_related('client', 'project', 'quotation', 'created_by')
            .prefetch_related('items', 'payments__recorded_by'),
            pk=self.kwargs['pk']
        )
        user = self.request.user
        if user.role == 'client':
            profile = getattr(user, 'client_profile', None)
            if not profile or obj.client != profile:
                from django.http import Http404
                raise Http404("Invoice not found")
        return obj

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['can_edit'] = self.request.user.role in ('admin', 'accountant')
        return ctx


class InvoiceDeleteView(LoginRequiredMixin, DeleteView):
    model = Invoice
    template_name = 'invoices/invoice_confirm_delete.html'
    success_url = reverse_lazy('invoices:list')
    context_object_name = 'inv'

    def delete(self, request, *args, **kwargs):
        inv = self.get_object()
        messages.success(request, f'Invoice {inv.invoice_number} deleted.')
        return super().delete(request, *args, **kwargs)


def invoice_pdf(request, pk):
    inv = get_object_or_404(
        Invoice.objects.select_related('client', 'project', 'created_by').prefetch_related('items'),
        pk=pk
    )
    from apps.core.models import CompanySettings
    company_settings = CompanySettings.objects.first()
    html = render_to_string('invoices/invoice_pdf.html', {
        'inv': inv,
        'company_settings': company_settings,
        'MEDIA_URL': settings.MEDIA_URL,
    })
    return HttpResponse(html)


@transaction.atomic
def record_payment(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.invoice = invoice
            payment.recorded_by = request.user
            payment.save()

            invoice.amount_paid += payment.amount
            invoice.balance = invoice.grand_total - invoice.amount_paid
            if invoice.balance <= Decimal('0.00'):
                invoice.status = 'Paid'
                invoice.balance = Decimal('0.00')
            else:
                invoice.status = 'Pending'
            invoice.save(update_fields=['amount_paid', 'balance', 'status'])

            messages.success(request, f'Payment of {payment.amount} recorded for {invoice.invoice_number}.')
            return redirect('invoices:detail', pk=invoice.pk)
    else:
        form = PaymentForm(initial={'payment_date': __import__('datetime').date.today()})

    return render(request, 'invoices/payment_form.html', {'form': form, 'invoice': invoice})
