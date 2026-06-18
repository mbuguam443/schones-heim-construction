from datetime import datetime

from django.db.models import Count

from .models import CompanySettings, Notification


def site_settings(request):
    ctx = {
        'site_name': 'SCHONES HEIM BUILDERS',
        'site_short_name': 'SHB',
        'current_year': datetime.now().year,
    }
    if request.user.is_authenticated:
        ctx['unread_count'] = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count()

        _inject_project_context(request, ctx)

        try:
            company = CompanySettings.objects.first()
            if company:
                ctx['company'] = company
                ctx['site_name'] = company.company_name
        except Exception:
            pass
    return ctx


def _inject_project_context(request, ctx):
    """Add active_client, active_project, and dropdown lists to context."""
    import json
    from apps.clients.models import Client
    from apps.projects.models import Project

    active_client_id = request.session.get('active_client_id')
    active_project_id = request.session.get('active_project_id')
    user = request.user

    # Auto-detect client for client users
    client_profile = None
    if user.role == 'client':
        client_profile = getattr(user, 'client_profile', None)
        if client_profile and not active_client_id:
            active_client_id = client_profile.pk
            request.session['active_client_id'] = active_client_id

    # Auto-detect project for store_keeper users based on their assignments
    if user.role == 'store_keeper' and not active_project_id:
        assignments = user.project_assignments.all()
        if assignments.count() == 1:
            active_project_id = assignments.first().project_id
            request.session['active_project_id'] = active_project_id
            active_client_id = assignments.first().project.client_id
            request.session['active_client_id'] = active_client_id

    # Clients available to this user
    if user.role == 'client':
        if client_profile:
            ctx['available_clients'] = Client.objects.filter(pk=client_profile.pk)
        else:
            ctx['available_clients'] = Client.objects.none()
    elif user.role == 'store_keeper':
        ctx['available_clients'] = Client.objects.none()
    else:
        ctx['available_clients'] = Client.objects.all().order_by('full_name')

    # All projects grouped by client (for JS dropdown dependency)
    all_user_projects = Project.objects.all().order_by('name')
    if user.role == 'client':
        profile = getattr(user, 'client_profile', None)
        if profile:
            all_user_projects = all_user_projects.filter(client=profile)
        else:
            all_user_projects = Project.objects.none()
    elif user.role == 'store_keeper':
        assignment_ids = user.project_assignments.values_list('project_id', flat=True)
        all_user_projects = all_user_projects.filter(pk__in=list(assignment_ids))

    project_map = {}
    for p in all_user_projects:
        cid = str(p.client_id)
        project_map.setdefault(cid, []).append({'pk': p.pk, 'name': p.name})
    ctx['project_map_json'] = json.dumps(project_map)

    # Projects (filtered by active client if set)
    project_qs = all_user_projects
    if active_client_id:
        project_qs = project_qs.filter(client_id=active_client_id)
        ctx['active_client'] = Client.objects.filter(pk=active_client_id).first()

    # Auto-select project if only one available and none selected
    if not active_project_id:
        project_list = list(project_qs[:2])
        if len(project_list) == 1:
            active_project_id = project_list[0].pk
            request.session['active_project_id'] = active_project_id

    ctx['available_projects'] = project_qs

    if active_project_id:
        ctx['active_project'] = Project.objects.filter(pk=active_project_id).first()
