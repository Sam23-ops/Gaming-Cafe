from functools import wraps
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from django.contrib import messages

def role_required(allowed_roles):
    """
    Decorator to restrict view to users having specific roles.
    allowed_roles: list or tuple of role codes (e.g., ['STAFF', 'MANAGER', 'ADMIN', 'SUPER_ADMIN'])
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, "Please log in to access this page.")
                return redirect(f"/accounts/login/?next={request.path}")
            
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            user_role = request.user.role.code if request.user.role else 'CUSTOMER'
            if user_role in allowed_roles:
                return view_func(request, *args, **kwargs)
            
            messages.error(request, "Access Denied: You do not have sufficient permissions to view this resource.")
            raise PermissionDenied("Access Denied: Insufficient Role Permissions")
        return _wrapped_view
    return decorator


def permission_required(perm_codename):
    """
    Decorator to enforce granular RBAC permissions.
    perm_codename: e.g. 'booking.cancel', 'game.create', 'report.view'
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, "Please log in to perform this action.")
                return redirect(f"/accounts/login/?next={request.path}")
            
            if request.user.is_superuser or request.user.has_custom_perm(perm_codename):
                return view_func(request, *args, **kwargs)
            
            messages.error(request, f"Access Denied: Missing required permission '{perm_codename}'.")
            raise PermissionDenied(f"Permission '{perm_codename}' is required.")
        return _wrapped_view
    return decorator
