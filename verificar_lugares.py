import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sgai.settings')
django.setup()

from inventario.models import Lugares

print(f"Total lugares: {Lugares.objects.count()}")
print(f"Lugares activos: {Lugares.objects.filter(activo=True).count()}")
print("\nPrimeros 10 lugares:")
print("-" * 80)

for lugar in Lugares.objects.all()[:10]:
    tipo = lugar.tipo_nivel.nombre if hasattr(lugar, 'tipo_nivel') and lugar.tipo_nivel else "Sin tipo"
    padre = lugar.padre.nombre if lugar.padre else "RAÍZ"
    print(f"ID: {lugar.id:3} | Nivel: {lugar.nivel} | Tipo: {tipo:20} | Padre: {padre:20} | Nombre: {lugar.nombre}")

print("\n" + "=" * 80)
print("Verificando campos del modelo:")
print("-" * 80)

primer_lugar = Lugares.objects.first()
if primer_lugar:
    print(f"Campos del primer lugar (ID: {primer_lugar.id}):")
    for field in primer_lugar._meta.fields:
        valor = getattr(primer_lugar, field.name, "N/A")
        print(f"  {field.name}: {valor}")
