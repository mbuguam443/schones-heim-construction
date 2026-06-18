from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.http import JsonResponse, HttpResponseRedirect
from django.db.models import Q
from .models import Project, ProjectAssignment, ProjectPhoto, ProjectDocument
from .forms import ProjectForm, ProjectAssignmentForm, ProjectPhotoForm, ProjectDocumentForm, ProjectProgressForm

UserModel = get_user_model()


def is_admin_or_pm(user):
    return user.role in ('admin', 'project_manager')


class AdminOrPMMixin(UserPassesTestMixin):
    def test_func(self):
        return is_admin_or_pm(self.request.user)


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related('client')
        user = self.request.user
        if user.role == 'client':
            profile = getattr(user, 'client_profile', None)
            if profile:
                qs = qs.filter(client=profile)
            else:
                qs = qs.none()
        q = self.request.GET.get('q', '').strip()
        status_filter = self.request.GET.get('status', '').strip()
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(client__full_name__icontains=q) | Q(location__icontains=q))
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search_query'] = self.request.GET.get('q', '')
        ctx['status_filter'] = self.request.GET.get('status', '')
        ctx['status_choices'] = Project.Status.choices
        ctx['can_edit'] = is_admin_or_pm(self.request.user)
        return ctx


class ProjectCreateView(LoginRequiredMixin, AdminOrPMMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'
    success_url = reverse_lazy('projects:project_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user
        if user.role == 'client':
            profile = getattr(user, 'client_profile', None)
            if not profile or obj.client != profile:
                from django.http import Http404
                raise Http404("Project not found")
        return obj

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        project = self.object
        ctx['assignments'] = project.assignments.select_related('employee').all()
        ctx['photos'] = project.photos.all()
        ctx['documents'] = project.documents.all()
        ctx['can_edit'] = is_admin_or_pm(self.request.user)
        ctx['photo_form'] = ProjectPhotoForm(initial={'project': project})
        ctx['document_form'] = ProjectDocumentForm(initial={'project': project})
        ctx['assignment_form'] = ProjectAssignmentForm()
        ctx['assignment_form'].fields['employee'].queryset = self._get_assignable_employees(project)
        ctx['progress_form'] = ProjectProgressForm(instance=project)
        return ctx

    def _get_assignable_employees(self, project):
        assigned_ids = project.assignments.values_list('employee_id', flat=True)
        return UserModel.objects.filter(role__in=('site_supervisor', 'employee')).exclude(id__in=assigned_ids)


class ProjectUpdateView(LoginRequiredMixin, AdminOrPMMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'
    success_url = reverse_lazy('projects:project_list')


class ProjectDeleteView(LoginRequiredMixin, AdminOrPMMixin, DeleteView):
    model = Project
    template_name = 'projects/project_confirm_delete.html'
    success_url = reverse_lazy('projects:project_list')


class ProjectProgressUpdateView(LoginRequiredMixin, AdminOrPMMixin, UpdateView):
    model = Project
    form_class = ProjectProgressForm

    def form_valid(self, form):
        form.save()
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'progress_percent': form.instance.progress_percent})
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('project_detail', kwargs={'pk': self.object.pk})


class ProjectAssignmentCreateView(LoginRequiredMixin, AdminOrPMMixin, CreateView):
    form_class = ProjectAssignmentForm

    def form_valid(self, form):
        form.instance.assigned_by = self.request.user
        form.instance.project_id = self.kwargs['pk']
        form.save()
        return HttpResponseRedirect(reverse('projects:project_detail', kwargs={'pk': self.kwargs['pk']}))

    def get_success_url(self):
        return reverse('projects:project_detail', kwargs={'pk': self.kwargs['pk']})


class ProjectAssignmentDeleteView(LoginRequiredMixin, AdminOrPMMixin, DeleteView):
    model = ProjectAssignment

    def get_success_url(self):
        return reverse('projects:project_detail', kwargs={'pk': self.object.project_id})


class ProjectPhotoCreateView(LoginRequiredMixin, AdminOrPMMixin, CreateView):
    form_class = ProjectPhotoForm

    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        form.instance.project_id = self.kwargs['pk']
        form.save()
        return HttpResponseRedirect(reverse('projects:project_detail', kwargs={'pk': self.kwargs['pk']}))

    def get_success_url(self):
        return reverse('projects:project_detail', kwargs={'pk': self.kwargs['pk']})


class ProjectDocumentCreateView(LoginRequiredMixin, AdminOrPMMixin, CreateView):
    form_class = ProjectDocumentForm

    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        form.instance.project_id = self.kwargs['pk']
        form.save()
        return HttpResponseRedirect(reverse('projects:project_detail', kwargs={'pk': self.kwargs['pk']}))

    def get_success_url(self):
        return reverse('projects:project_detail', kwargs={'pk': self.kwargs['pk']})
