def filter_by_active_project(request, queryset):
    """Filter a queryset by the active project or client context.
    
    - If a project is selected: filter to that project only
    - If only a client is selected: filter to all projects of that client
    - Otherwise: return unfiltered
    
    Call this in get_queryset() of any ListView whose model has a `project` FK.
    """
    project_id = request.session.get('active_project_id')
    client_id = request.session.get('active_client_id')

    if project_id:
        return queryset.filter(project_id=project_id)
    if client_id:
        from apps.projects.models import Project
        project_ids = Project.objects.filter(client_id=client_id).values_list('pk', flat=True)
        return queryset.filter(project_id__in=list(project_ids))
    return queryset


def get_active_project(request):
    """Return the active Project object from session, or None."""
    from apps.projects.models import Project
    project_id = request.session.get('active_project_id')
    if project_id:
        try:
            return Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            return None
    return None


def get_active_client(request):
    """Return the active Client object from session, or None."""
    from apps.clients.models import Client
    client_id = request.session.get('active_client_id')
    if client_id:
        try:
            return Client.objects.get(pk=client_id)
        except Client.DoesNotExist:
            return None
    return None
