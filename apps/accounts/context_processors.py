def user_role_context(request):
    """
    Expose user role, staff status, admin status, and permission helper to templates.
    """
    if not request.user.is_authenticated:
        return {
            'CURRENT_ROLE': 'GUEST',
            'IS_STAFF_MEMBER': False,
            'IS_ADMIN_MEMBER': False,
            'IS_SUPER_ADMIN': False,
            'USER_LOYALTY_POINTS': 0,
        }

    user = request.user
    role_code = user.role_code

    return {
        'CURRENT_ROLE': role_code,
        'IS_STAFF_MEMBER': user.is_staff_member,
        'IS_ADMIN_MEMBER': user.is_admin_member,
        'IS_SUPER_ADMIN': user.is_superuser or role_code == 'SUPER_ADMIN',
        'USER_LOYALTY_POINTS': user.loyalty_points,
        'USER_GAMER_TAG': user.gamer_tag or user.username,
    }
