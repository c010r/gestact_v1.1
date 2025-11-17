from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse

from .models import (
	Estado,
	TipoNivel,
	Lugares,
	TipoComputadora,
	TipoImpresora,
	Fabricante,
	Modelo,
	TipoGarantia,
	TipoInsumo,
	Insumo,
	Impresora,
	Computadora,
	Proveedor,
	Factura,
	FacturaActivo,
	TipoTecnologiaMedica,
	TecnologiaMedica,
	Bitacora,
)
from .utils_reports import (
	SEGMENT_INFORMATICA,
	SEGMENT_MEDICA,
	gather_enterprise_report,
)


class RemitoTonerExtraTests(TestCase):
	def setUp(self):
		self.estado_stock = Estado.objects.create(nombre='Stock')

		self.tipo_nivel = TipoNivel.objects.create(nombre='Depósito', nivel=1)
		self.lugar_origen = Lugares.objects.create(
			nombre='Depósito Central',
			tipo_nivel=self.tipo_nivel,
		)
		self.lugar_destino = Lugares.objects.create(
			nombre='Hospital Central',
			tipo_nivel=self.tipo_nivel,
		)

		self.tipo_impresora = TipoImpresora.objects.create(nombre='Láser')
		self.fabricante = Fabricante.objects.create(nombre='HP')
		self.modelo = Modelo.objects.create(
			nombre='LaserJet 1020',
			fabricante=self.fabricante,
		)
		self.tipo_garantia = TipoGarantia.objects.create(nombre='Estándar')

		self.tipo_insumo = TipoInsumo.objects.create(nombre='Tóner', unidad_medida_default='unidad')
		self.insumo = Insumo.objects.create(
			nombre='Tóner 12A',
			tipo_insumo=self.tipo_insumo,
			cantidad_total=10,
			cantidad_disponible=5,
			punto_reorden=2,
			unidad_medida='unidad',
		)

		self.impresora = Impresora.objects.create(
			nombre='HP-1020',
			estado=self.estado_stock,
			lugar=self.lugar_origen,
			tipo_impresora=self.tipo_impresora,
			fabricante=self.fabricante,
			modelo=self.modelo,
			numero_serie='SN-1020',
			numero_inventario='INV-1020',
			tipo_garantia=self.tipo_garantia,
			fecha_adquisicion=date(2024, 1, 1),
			anos_garantia=1,
			valor_adquisicion=1500,
			moneda='UYU',
			requiere_toner_extra=True,
			insumo_toner_extra=self.insumo,
			cantidad_toner_extra=1,
		)

	def _set_carrito(self, lugar_destino_id):
		session = self.client.session
		session['facturacion_carrito'] = {
			'items': {
				'impresora': {
					str(self.impresora.pk): {
						'id': self.impresora.pk,
						'tipo': 'impresora',
					}
				}
			},
			'lugar_destino_id': lugar_destino_id,
			'observaciones': 'Entrega con tóner',
		}
		session.save()

	def test_emitir_remito_descuenta_toner_extra(self):
		self._set_carrito(self.lugar_destino.pk)

		response = self.client.post(
			reverse('inventario:facturacion_emitir'),
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response['Content-Type'], 'application/pdf')

		self.impresora.refresh_from_db()
		self.insumo.refresh_from_db()

		self.assertEqual(self.impresora.estado, self.estado_stock)
		self.assertEqual(self.impresora.lugar, self.lugar_destino)
		self.assertEqual(self.insumo.cantidad_disponible, 4)

		factura = Factura.objects.first()
		self.assertIsNotNone(factura)

		activos_impresora = factura.activos.filter(tipo_activo=FacturaActivo.IMPRESORA)
		self.assertEqual(activos_impresora.count(), 1)

		activos_insumo = factura.activos.filter(tipo_activo=FacturaActivo.INSUMO)
		self.assertEqual(activos_insumo.count(), 1)
		self.assertEqual(activos_insumo.first().cantidad, 1)

	def test_emitir_remito_falla_sin_stock_toner(self):
		self.insumo.cantidad_disponible = 0
		self.insumo.save(update_fields=['cantidad_disponible'])

		self._set_carrito(self.lugar_destino.pk)

		response = self.client.post(
			reverse('inventario:facturacion_emitir'),
		)

		self.assertEqual(response.status_code, 400)
		data = response.json()
		self.assertFalse(data['success'])
		self.assertIn('stock suficiente', data['error'])

		self.assertEqual(Factura.objects.count(), 0)
		self.impresora.refresh_from_db()
		self.assertEqual(self.impresora.lugar, self.lugar_origen)
		self.assertEqual(self.impresora.estado, self.estado_stock)
		self.insumo.refresh_from_db()
		self.assertEqual(self.insumo.cantidad_disponible, 0)


class ComputadoraUpdateViewTests(TestCase):
	def setUp(self):
		self.estado_operativo = Estado.objects.create(nombre='Operativo')
		self.estado_stock = Estado.objects.create(nombre='Stock')
		self.tipo_computadora = TipoComputadora.objects.create(nombre='Desktop')
		self.tipo_nivel = TipoNivel.objects.create(nombre='Depósito', nivel=1)
		self.lugar = Lugares.objects.create(nombre='Depósito Central', tipo_nivel=self.tipo_nivel)
		self.fabricante = Fabricante.objects.create(nombre='HP')
		self.modelo = Modelo.objects.create(nombre='EliteDesk', fabricante=self.fabricante)
		self.tipo_garantia = TipoGarantia.objects.create(nombre='Fabricante')
		self.proveedor = Proveedor.objects.create(nombre='TechSupply')

		self.computadora = Computadora.objects.create(
			nombre='HP-ED-1',
			estado=self.estado_operativo,
			lugar=self.lugar,
			tipo_computadora=self.tipo_computadora,
			fabricante=self.fabricante,
			modelo=self.modelo,
			numero_serie='SN-0001',
			numero_inventario='INV-0001',
			tipo_garantia=self.tipo_garantia,
			fecha_adquisicion=date(2024, 1, 1),
			anos_garantia=3,
			proveedor=self.proveedor,
		)

	def test_actualizar_estado(self):
		url = reverse('inventario:computadora_update', kwargs={'pk': self.computadora.pk})
		list_url = reverse('inventario:computadora_list')
		response = self.client.post(
			url,
			{
				'nombre': 'HP-ED-1',
				'estado': self.estado_stock.pk,
				'lugar': self.lugar.pk,
				'tipo_computadora': self.tipo_computadora.pk,
				'fabricante': self.fabricante.pk,
				'modelo': self.modelo.pk,
				'numero_serie': 'SN-0001',
				'numero_inventario': 'INV-0001',
				'proveedor': self.proveedor.pk,
				'tipo_garantia': self.tipo_garantia.pk,
				'fecha_adquisicion': '2024-01-01',
				'anos_garantia': 3,
				'valor_adquisicion': '',
				'moneda': 'UYU',
				'comentarios': '',
				'monitores_vinculados': [],
				'impresoras_vinculadas': [],
				'next': list_url,
			},
		)
		self.assertRedirects(response, list_url)
		self.computadora.refresh_from_db()
		self.assertEqual(self.computadora.estado, self.estado_stock)


class ReportSegmentationTests(TestCase):
	def setUp(self):
		self.estado_activo = Estado.objects.create(nombre='Activo')
		self.tipo_nivel = TipoNivel.objects.create(nombre='Hospital', nivel=1)
		self.lugar = Lugares.objects.create(nombre='Hospital Central', tipo_nivel=self.tipo_nivel)
		self.tipo_computadora = TipoComputadora.objects.create(nombre='All in One')
		self.tipo_tecnologia = TipoTecnologiaMedica.objects.create(nombre='Respirador')
		self.fabricante = Fabricante.objects.create(nombre='MedTech')
		self.modelo = Modelo.objects.create(nombre='Serie X', fabricante=self.fabricante)
		self.tipo_garantia = TipoGarantia.objects.create(nombre='Garantía Anual')
		self.proveedor = Proveedor.objects.create(nombre='Proveedor General')

		fecha_base = date.today() - timedelta(days=200)

		self.computadora = Computadora.objects.create(
			nombre='PC-SEG-1',
			estado=self.estado_activo,
			lugar=self.lugar,
			tipo_computadora=self.tipo_computadora,
			fabricante=self.fabricante,
			modelo=self.modelo,
			numero_serie='SEG-PC-001',
			numero_inventario='SEG-PC-001',
			tipo_garantia=self.tipo_garantia,
			fecha_adquisicion=fecha_base,
			anos_garantia=1,
			valor_adquisicion=1500,
			moneda='UYU',
			proveedor=self.proveedor,
		)

		self.equipo_medico = TecnologiaMedica.objects.create(
			nombre='Respirador Alpha',
			estado=self.estado_activo,
			lugar=self.lugar,
			tipo_tecnologia_medica=self.tipo_tecnologia,
			fabricante=self.fabricante,
			modelo=self.modelo,
			numero_serie='SEG-MED-001',
			tipo_garantia=self.tipo_garantia,
			fecha_adquisicion=fecha_base,
			anos_garantia=1,
			valor_adquisicion=3500,
			moneda='UYU',
			proveedor=self.proveedor,
			requiere_mantenimiento_preventivo=True,
			frecuencia_mantenimiento_meses=12,
		)

		Bitacora.objects.create(
			tipo_evento='baja',
			tipo_dispositivo='computadora',
			dispositivo_id=self.computadora.pk,
			dispositivo_nombre=self.computadora.nombre,
			descripcion='Baja de prueba TI',
		)

		Bitacora.objects.create(
			tipo_evento='baja',
			tipo_dispositivo='tecnologia_medica',
			dispositivo_id=self.equipo_medico.pk,
			dispositivo_nombre=self.equipo_medico.nombre,
			descripcion='Baja de prueba médica',
		)

	def test_medical_segment_excludes_it_assets(self):
		report = gather_enterprise_report(None, None, segment=SEGMENT_MEDICA)

		tipos_compra = {item['tipo'] for item in report['annual_purchases']}
		self.assertIn('Tecnología Médica', tipos_compra)
		self.assertNotIn('Computadoras', tipos_compra)

		bajas_tipos = {item['tipo_dispositivo'] for item in report['bajas']['detalle']}
		self.assertEqual(bajas_tipos, {'tecnologia_medica'})

	def test_it_segment_excludes_medical_assets(self):
		report = gather_enterprise_report(None, None, segment=SEGMENT_INFORMATICA)

		tipos_compra = {item['tipo'] for item in report['annual_purchases']}
		self.assertIn('Computadoras', tipos_compra)
		self.assertNotIn('Tecnología Médica', tipos_compra)

		bajas_tipos = {item['tipo_dispositivo'] for item in report['bajas']['detalle']}
		self.assertEqual(bajas_tipos, {'computadora'})

