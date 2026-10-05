from .models import AuditLog

def get_client_ip(request):
    if not request:
        return None
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def log_action(request_or_user, action_type, entity_name, entity_id='', description='', metadata=None):
    """
    Log an administrative, operational or financial action to the immutable audit trail.
    """
    actor = None
    actor_name = 'System'
    actor_role = 'System'
    ip_address = None

    if hasattr(request_or_user, 'user'):
        request = request_or_user
        if request.user.is_authenticated:
            actor = request.user
            actor_name = actor.get_full_name() or actor.username or actor.gamer_tag or str(actor)
            actor_role = actor.role.name if hasattr(actor, 'role') and actor.role else ('Super Admin' if actor.is_superuser else 'User')
        else:
            actor_name = 'Anonymous'
            actor_role = 'Guest'
        ip_address = get_client_ip(request)
    elif request_or_user and hasattr(request_or_user, 'is_authenticated'):
        actor = request_or_user
        actor_name = actor.get_full_name() or actor.username or actor.gamer_tag or str(actor)
        actor_role = actor.role.name if hasattr(actor, 'role') and actor.role else ('Super Admin' if actor.is_superuser else 'User')

    return AuditLog.objects.create(
        actor=actor,
        actor_name=actor_name,
        actor_role=actor_role,
        action_type=action_type,
        entity_name=entity_name,
        entity_id=str(entity_id),
        description=description,
        ip_address=ip_address,
        metadata=metadata or {}
    )
