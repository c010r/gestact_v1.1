from django.db import migrations


def rename_en_bodega_to_almacen(apps, schema_editor):
    Estado = apps.get_model('inventario', 'Estado')

    estado_bodega = Estado.objects.filter(nombre__iexact='En bodega').first()
    if estado_bodega:
        estado_bodega.nombre = 'Almacen'
        estado_bodega.save(update_fields=['nombre'])


def revert_to_en_bodega(apps, schema_editor):
    Estado = apps.get_model('inventario', 'Estado')

    estado_almacen = Estado.objects.filter(nombre__iexact='Almacen').first()
    if estado_almacen:
        estado_almacen.nombre = 'En bodega'
        estado_almacen.save(update_fields=['nombre'])


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0016_impresora_toner_extra_facturaactivo_cantidad'),
    ]

    operations = [
        migrations.RunPython(rename_en_bodega_to_almacen, revert_to_en_bodega),
    ]