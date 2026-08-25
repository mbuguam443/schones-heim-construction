from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, View
from django.shortcuts import get_object_or_404, redirect, render
from django.http import FileResponse
from django.db.models import Q
from apps.core.mixins import filter_by_active_project
from .models import Document, DocumentCategory, CompanyDocument
from .forms import DocumentForm, DocumentCategoryForm, CompanyDocumentForm


def can_edit_docs(user):
    return user.role in ('admin', 'project_manager')


class AdminOrPMDocMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        return can_edit_docs(self.request.user)


class DocumentListView(LoginRequiredMixin, ListView):
    model = Document
    template_name = 'documents/document_list.html'
    context_object_name = 'documents'

    def get_queryset(self):
        qs = super().get_queryset()
        cancelled = self.request.GET.get('cancelled')
        if cancelled != '1':
            qs = qs.filter(is_active=True)
        qs = filter_by_active_project(self.request, qs)
        user = self.request.user
        if user.role == 'client':
            profile = getattr(user, 'client_profile', None)
            if profile:
                qs = qs.filter(Q(project__client=profile) | Q(project__isnull=True))
            else:
                qs = qs.none()
        category = self.request.GET.get('category')
        if category:
            qs = qs.filter(category_id=category)
        return qs.select_related('category', 'project', 'uploaded_by')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = DocumentCategory.objects.all()
        context['can_edit'] = can_edit_docs(self.request.user)
        context['show_cancelled'] = self.request.GET.get('cancelled') == '1'
        context['cancelled_count'] = Document.objects.filter(is_active=False).count()
        return context


class DocumentCreateView(LoginRequiredMixin, AdminOrPMDocMixin, CreateView):
    model = Document
    form_class = DocumentForm
    template_name = 'documents/document_form.html'
    success_url = reverse_lazy('documents:document_list')

    def get_initial(self):
        initial = super().get_initial()
        from apps.core.mixins import get_active_project
        proj = get_active_project(self.request)
        if proj:
            initial['project'] = proj
        return initial

    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        return super().form_valid(form)


class DocumentUpdateView(LoginRequiredMixin, AdminOrPMDocMixin, UpdateView):
    model = Document
    form_class = DocumentForm
    template_name = 'documents/document_form.html'
    success_url = reverse_lazy('documents:document_list')


class DocumentCancelView(LoginRequiredMixin, View):
    def get(self, request, pk):
        doc = get_object_or_404(Document, pk=pk)
        doc.cancel()
        messages.success(request, f'Document "{doc.title}" cancelled.')
        return redirect('documents:document_list')


class DocumentRestoreView(LoginRequiredMixin, View):
    def get(self, request, pk):
        doc = get_object_or_404(Document, pk=pk)
        doc.restore()
        messages.success(request, f'Document "{doc.title}" restored.')
        return redirect('documents:document_list')


class DocumentDownloadView(LoginRequiredMixin, View):
    def get(self, request, pk):
        document = get_object_or_404(Document, pk=pk)
        response = FileResponse(document.file.open('rb'), as_attachment=True, filename=document.filename())
        return response


class DocumentCategoryListView(LoginRequiredMixin, ListView):
    model = DocumentCategory
    template_name = 'documents/documentcategory_list.html'
    context_object_name = 'categories'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .forms import DocumentCategoryForm
        context['can_edit'] = can_edit_docs(self.request.user)
        context['categories'] = DocumentCategory.objects.all()
        context['form'] = DocumentCategoryForm()
        qs = Document.objects.all().select_related('category', 'project', 'uploaded_by')
        user = self.request.user
        if user.role == 'client':
            profile = getattr(user, 'client_profile', None)
            if profile:
                qs = qs.filter(Q(project__client=profile) | Q(project__isnull=True))
            else:
                qs = qs.none()
        context['documents'] = qs
        return context


class CompanyDocumentListView(LoginRequiredMixin, ListView):
    model = CompanyDocument
    template_name = 'documents/company_document_list.html'
    context_object_name = 'documents'
    paginate_by = 15

    def get_queryset(self):
        qs = super().get_queryset().select_related('project', 'created_by')
        doc_type = self.request.GET.get('type')
        status = self.request.GET.get('status')
        if doc_type:
            qs = qs.filter(doc_type=doc_type)
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_edit'] = can_edit_docs(self.request.user)
        context['current_type'] = self.request.GET.get('type', '')
        context['current_status'] = self.request.GET.get('status', '')
        return context


class CompanyDocumentCreateView(LoginRequiredMixin, AdminOrPMDocMixin, CreateView):
    model = CompanyDocument
    form_class = CompanyDocumentForm
    template_name = 'documents/company_document_form.html'
    success_url = reverse_lazy('documents:company_document_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editing'] = False
        return context


class CompanyDocumentUpdateView(LoginRequiredMixin, AdminOrPMDocMixin, UpdateView):
    model = CompanyDocument
    form_class = CompanyDocumentForm
    template_name = 'documents/company_document_form.html'
    success_url = reverse_lazy('documents:company_document_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editing'] = True
        return context


class CompanyDocumentDeleteView(LoginRequiredMixin, AdminOrPMDocMixin, View):
    def post(self, request, pk):
        doc = get_object_or_404(CompanyDocument, pk=pk)
        doc.delete()
        messages.success(request, f'Document "{doc.title}" deleted.')
        return redirect('documents:company_document_list')


class CompanyDocumentPreviewView(LoginRequiredMixin, View):
    def get(self, request, pk):
        doc = get_object_or_404(CompanyDocument, pk=pk)
        from apps.core.models import CompanySettings
        company = CompanySettings.objects.first()
        signature_data_uri = None
        if doc.show_signature:
            try:
                import base64, os
                from django.conf import settings as django_settings
                sig_path = os.path.join(django_settings.STATIC_ROOT or '', 'newSignature.png')
                if not os.path.exists(sig_path):
                    sig_path = os.path.join(str(django_settings.STATICFILES_DIRS[0]) if django_settings.STATICFILES_DIRS else '', 'newSignature.png')
                if os.path.exists(sig_path):
                    with open(sig_path, 'rb') as f:
                        sig_data = base64.b64encode(f.read()).decode('utf-8')
                    signature_data_uri = f'data:image/png;base64,{sig_data}'
            except Exception:
                pass
        return render(request, 'documents/company_document_preview.html', {
            'doc': doc,
            'company': company,
            'signature_data_uri': signature_data_uri,
        })
