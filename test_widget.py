import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sgai.settings')
django.setup()

from inventario.widgets import TreeSelectWidget
from inventario.models import Lugares

# Crear instancia del widget
widget = TreeSelectWidget()

# Simular contexto
context = widget.get_context('lugar', None, {})

print("Tree data generado por el widget:")
print("=" * 80)
print(context.get('tree_data', 'NO HAY DATOS'))
print("=" * 80)

if 'error' in context:
    print(f"\nERROR: {context['error']}")
else:
    import json
    try:
        datos = json.loads(context['tree_data'])
        print(f"\nTotal lugares en JSON: {len(datos)}")
        print("\nPrimeros 3 lugares:")
        for lugar in datos[:3]:
            print(f"  ID: {lugar['id']} | Nivel: {lugar['nivel']} | Nombre: {lugar['nombre']}")
    except Exception as e:
        print(f"Error al parsear JSON: {e}")
