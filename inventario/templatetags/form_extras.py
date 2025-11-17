"""Filtros personalizados para manejo de formularios en plantillas."""
from django import forms
from django import template

register = template.Library()


@register.filter(name="is_checkbox")
def is_checkbox(field):
    """Return True when field renders with a checkbox widget."""
    widget = getattr(getattr(field, "field", None), "widget", None)
    return isinstance(widget, forms.CheckboxInput)


@register.filter(name="is_textarea")
def is_textarea(field):
    """Return True when field renders with a textarea widget."""
    widget = getattr(getattr(field, "field", None), "widget", None)
    return isinstance(widget, forms.Textarea)
