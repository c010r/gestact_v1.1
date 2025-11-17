from django.db import migrations

MODELOS_ESTADO = [
    ("inventario", "Computadora"),
    ("inventario", "Impresora"),
    ("inventario", "Monitor"),
    ("inventario", "Networking"),
    ("inventario", "Telefonia"),
    ("inventario", "Periferico"),
    ("inventario", "Software"),
    ("inventario", "PlantillaDispositivo"),
]


def _actualizar_referencias(apps, origen_id, destino_id):
    for app_label, model_name in MODELOS_ESTADO:
        Model = apps.get_model(app_label, model_name)
        Model.objects.filter(estado_id=origen_id).update(estado_id=destino_id)


def rename_almacen_to_stock(apps, schema_editor):
    Estado = apps.get_model("inventario", "Estado")

    almacen_estados = list(Estado.objects.filter(nombre__iexact="Almacen"))
    almacenes_adicionales = Estado.objects.filter(nombre__iexact="Almacén")
    for estado in almacenes_adicionales:
        if estado not in almacen_estados:
            almacen_estados.append(estado)

    if not almacen_estados:
        return

    stock_estado = Estado.objects.filter(nombre__iexact="Stock").first()

    if not stock_estado:
        principal = almacen_estados[0]
        principal.nombre = "Stock"
        if not principal.comentarios:
            principal.comentarios = "Dispositivo disponible en stock"
        principal.save(update_fields=["nombre", "comentarios"])
        stock_estado = principal
        restantes = almacen_estados[1:]
    else:
        restantes = almacen_estados

    for estado in restantes:
        if estado.pk == stock_estado.pk:
            continue
        _actualizar_referencias(apps, estado.pk, stock_estado.pk)
        estado.delete()


def revert_stock_to_almacen(apps, schema_editor):
    Estado = apps.get_model("inventario", "Estado")

    stock_estados = list(Estado.objects.filter(nombre__iexact="Stock"))
    if not stock_estados:
        return

    almacen_existente = Estado.objects.filter(nombre__iexact="Almacen").first()
    if almacen_existente:
        return

    principal = stock_estados[0]
    principal.nombre = "Almacen"
    principal.save(update_fields=["nombre"])


class Migration(migrations.Migration):

    dependencies = [
        ("inventario", "0017_rename_en_bodega_to_almacen"),
    ]

    operations = [
        migrations.RunPython(rename_almacen_to_stock, revert_stock_to_almacen),
    ]
