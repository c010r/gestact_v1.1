"""
Context processors for the inventario app.
Injects user access level into every template rendered with a request context.
"""

# Group name → module key mapping
MODULE_GROUPS = {
    'Activos Informáticos': 'informatica',
    'Tecnología Médica': 'medica',
    'Activos Generales': 'generales',
    'Administrador': 'admin',
}

FULL_ACCESS_GROUP = 'Administrador'


def user_access(request):
    """
    Adds to every template context:
      - is_full_access (bool): True if user belongs to 'Administrador' or is superuser
      - user_module (str | None): the module key for the user's primary group
      - user_groups_names (list[str]): names of all groups the user belongs to
    """
    if not hasattr(request, 'user') or not request.user.is_authenticated:
        return {
            'is_full_access': False,
            'user_module': None,
            'user_groups_names': [],
        }

    user = request.user

    # Superusers always have full access
    if user.is_superuser:
        return {
            'is_full_access': True,
            'user_module': 'admin',
            'user_groups_names': list(user.groups.values_list('name', flat=True)),
        }

    group_names = list(user.groups.values_list('name', flat=True))

    is_full_access = FULL_ACCESS_GROUP in group_names

    # Determine primary module (first matching group in priority order)
    user_module = None
    for group_name, module_key in MODULE_GROUPS.items():
        if group_name in group_names:
            user_module = module_key
            break

    return {
        'is_full_access': is_full_access,
        'user_module': user_module,
        'user_groups_names': group_names,
    }
