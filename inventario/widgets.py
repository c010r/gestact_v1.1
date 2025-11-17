"""
Widgets personalizados para el sistema de inventario
"""
from django import forms
from django.utils.safestring import mark_safe
import json


class HierarchicalSelectWidget(forms.Select):
    """
    Widget personalizado para seleccionar lugares de forma jerárquica
    Muestra los lugares organizados por niveles con indentación
    """
    template_name = 'inventario/widgets/hierarchical_select.html'

    def __init__(self, attrs=None, choices=()):
        default_attrs = {
            'class': 'form-control hierarchical-select',
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, choices=choices)

    def create_option(self, name, value, label, selected, index,
                      subindex=None, attrs=None):
        """Personaliza cada opción del select"""
        option = super().create_option(
            name, value, label, selected, index,
            subindex=subindex, attrs=attrs
        )

        # Si el valor no está vacío, intentamos obtener el nivel
        if value and value != '':
            try:
                from inventario.models import Lugares
                lugar = Lugares.objects.get(pk=value)
                
                # Calcular indentación basada en el nivel
                indent = '&nbsp;&nbsp;&nbsp;&nbsp;' * (lugar.nivel - 1)
                
                # Agregar indicadores visuales según el nivel
                iconos = {
                    1: '📁',
                    2: '🏢',
                    3: '🏥',
                    4: '📋',
                    5: '🔧',
                    6: '📍',
                    7: '💺'
                }
                
                prefix = iconos.get(lugar.nivel, '├─') + ' '
                
                # Construir el label con indentación y prefijo
                option['label'] = mark_safe(
                    f"{indent}{prefix}{lugar.nombre}"
                )
                
                # Agregar atributos de datos para uso en JavaScript
                option['attrs']['data-nivel'] = lugar.nivel
                option['attrs']['data-tipo'] = (
                    lugar.tipo_nivel.nombre if lugar.tipo_nivel 
                    else f'Nivel {lugar.nivel}'
                )
                option['attrs']['data-padre'] = (
                    lugar.padre.pk if lugar.padre else ''
                )
                
                # Agregar clase CSS según el nivel
                current_class = option['attrs'].get('class', '')
                option['attrs']['class'] = (
                    f"{current_class} nivel-{lugar.nivel}".strip()
                )
                
            except Exception:
                pass

        return option

    def optgroups(self, name, value, attrs=None):
        """Organiza las opciones en grupos jerárquicos"""
        groups = super().optgroups(name, value, attrs)
        return groups


class TreeSelectWidget(forms.Select):
    """
    Widget de selección con vista de árbol interactiva
    Requiere JavaScript para funcionar completamente
    """
    template_name = 'inventario/widgets/tree_select.html'

    class Media:
        css = {
            'all': ('inventario/css/tree-select.css',)
        }
        js = ('inventario/js/tree-select.js',)

    def __init__(self, attrs=None, choices=()):
        default_attrs = {
            'class': 'form-control tree-select-widget',
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, choices=choices)

    def get_context(self, name, value, attrs):
        """Prepara el contexto para el template"""
        context = super().get_context(name, value, attrs)
        
        # Construir estructura de árbol para JavaScript
        try:
            from inventario.models import Lugares, TipoNivel
            lugares = Lugares.objects.select_related(
                'padre', 'tipo_nivel'
            ).filter(activo=True).order_by('nivel', 'nombre')
            
            # Convertir a estructura JSON para el árbol
            tree_data = []
            for lugar in lugares:
                # Determinar si es hoja (no tiene hijos)
                es_hoja = not lugar.hijos.exists()
                
                tree_data.append({
                    'id': lugar.pk,
                    'nombre': lugar.nombre,
                    'nombre_completo': lugar.nombre_completo or lugar.nombre,
                    'nivel': lugar.nivel,
                    'tipo': lugar.tipo_nivel.nombre if lugar.tipo_nivel else f'Nivel {lugar.nivel}',
                    'tipo_nivel_id': lugar.tipo_nivel_id,
                    'tipo_nivel_requiere_codigo': (
                        bool(lugar.tipo_nivel.requiere_codigo)
                        if lugar.tipo_nivel
                        else False
                    ),
                    'padre_id': lugar.padre.pk if lugar.padre else None,
                    'es_hoja': es_hoja,
                    'codigo': lugar.codigo or '',
                    'activo': lugar.activo,
                })
            
            context['tree_data'] = json.dumps(tree_data)
            context['selected_value'] = value

            tipo_niveles = (
                TipoNivel.objects.filter(activo=True)
                .order_by('nivel')
            )
            context['tipo_niveles_data'] = json.dumps([
                {
                    'id': tipo.pk,
                    'nivel': tipo.nivel,
                    'nombre': tipo.nombre,
                    'requiere_codigo': tipo.requiere_codigo,
                }
                for tipo in tipo_niveles
            ])
            
        except Exception as e:
            context['tree_data'] = '[]'
            context['tipo_niveles_data'] = '[]'
            context['error'] = str(e)
        
        return context
