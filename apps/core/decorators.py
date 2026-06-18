from functools import wraps

from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('core:login')
            if request.user.role not in roles:
                raise PermissionDenied(_('You do not have permission to access this page.'))
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
