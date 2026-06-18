from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, View
from django.shortcuts import get_object_or_404, redirect
from django.http import FileResponse
from django.db.models import Q
from apps.core.mixins import filter_by_active_project
from .models import Document, DocumentCategory
from .forms import DocumentForm, DocumentCategoryForm


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
