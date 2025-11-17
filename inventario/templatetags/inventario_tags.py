"""Custom template tags for inventario app."""
from django import template
from inventario.models import Proveedor

register = template.Library()


@register.simple_tag
def get_proveedores():
    """Return all active providers ordered by name."""
    return Proveedor.objects.all().order_by('nombre')

