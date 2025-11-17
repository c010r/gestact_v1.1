from datetime import date

from django.test import TestCase
from django.urls import reverse

from inventario.models import (
    Computadora,
    Estado,
    TipoComputadora,
    Fabricante,
    Modelo,
    TipoGarantia,
    Proveedor,
    Lugares,
    TipoNivel,
)


class ComputadoraUpdateViewTests(TestCase):
    def setUp(self):
        self.estado = Estado.objects.create(nombre="Operativo")
        self.estado_stock = Estado.objects.create(nombre="Stock")
        self.tipo_computadora = TipoComputadora.objects.create(nombre="Desktop")
        self.tipo_nivel = TipoNivel.objects.create(nombre="Unidad Ejecutora", nivel=1)
        self.lugar = Lugares.objects.create(nombre="Depósito Central", tipo_nivel=self.tipo_nivel)
        self.fabricante = Fabricante.objects.create(nombre="HP")
        self.modelo = Modelo.objects.create(nombre="EliteDesk", fabricante=self.fabricante)
        self.tipo_garantia = TipoGarantia.objects.create(nombre="Fabricante")
        self.proveedor = Proveedor.objects.create(nombre="TechSupply")

        self.computadora = Computadora.objects.create(
            nombre="HP-ED-1",
            estado=self.estado,
            lugar=self.lugar,
            tipo_computadora=self.tipo_computadora,
            fabricante=self.fabricante,
            modelo=self.modelo,
            numero_serie="SN-0001",
            numero_inventario="INV-0001",
            proveedor=self.proveedor,
            tipo_garantia=self.tipo_garantia,
            fecha_adquisicion=date(2024, 1, 1),
            anos_garantia=3,
        )

    def test_update_estado(self):
        url = reverse("inventario:computadora_update", kwargs={"pk": self.computadora.pk})
        response = self.client.post(
            url,
            {
                "nombre": "HP-ED-1",
                "estado": self.estado_stock.pk,
                "lugar": self.lugar.pk,
                "tipo_computadora": self.tipo_computadora.pk,
                "fabricante": self.fabricante.pk,
                "modelo": self.modelo.pk,
                "numero_serie": "SN-0001",
                "numero_inventario": "INV-0001",
                "proveedor": self.proveedor.pk,
                "tipo_garantia": self.tipo_garantia.pk,
                "fecha_adquisicion": "2024-01-01",
                "anos_garantia": 3,
                "monitores_vinculados": [],
                "impresoras_vinculadas": [],
            },
        )
        self.assertEqual(response.status_code, 302)
        self.computadora.refresh_from_db()
        self.assertEqual(self.computadora.estado, self.estado_stock)
