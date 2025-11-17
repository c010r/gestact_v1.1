"""
Comando para crear datos de ejemplo del sistema jerárquico de lugares
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from inventario.models import TipoNivel, Lugares


class Command(BaseCommand):
    help = 'Crea datos de ejemplo para el sistema jerárquico de lugares'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING(
            '\n=== Creando Estructura Jerárquica de Ejemplo ==='
        ))

        try:
            with transaction.atomic():
                # Verificar que existan los tipos de nivel
                tipos = {
                    nivel.nivel: nivel
                    for nivel in TipoNivel.objects.all()
                }

                if len(tipos) != 7:
                    self.stdout.write(self.style.ERROR(
                        'Error: Debe ejecutar primero: '
                        'python manage.py init_tipos_nivel'
                    ))
                    return

                # Limpiar lugares existentes
                Lugares.objects.all().delete()
                self.stdout.write(self.style.SUCCESS(
                    '✓ Lugares anteriores eliminados'
                ))

                # NIVEL 1: Unidades Ejecutoras
                ue_hospital = Lugares.objects.create(
                    codigo='001',
                    nombre='Hospital Regional',
                    tipo_nivel=tipos[1],
                    comentarios='Hospital Regional de Alta Complejidad',
                    activo=True
                )

                ue_centro = Lugares.objects.create(
                    codigo='002',
                    nombre='Centro de Salud Norte',
                    tipo_nivel=tipos[1],
                    comentarios='Centro de Atención Primaria',
                    activo=True
                )

                self.stdout.write(self.style.SUCCESS(
                    f'✓ Creadas {Lugares.objects.filter(nivel=1).count()} '
                    'Unidades Ejecutoras'
                ))

                # NIVEL 2: Unidades Asistenciales (bajo Hospital)
                ua_cirugia = Lugares.objects.create(
                    nombre='Cirugía',
                    padre=ue_hospital,
                    tipo_nivel=tipos[2],
                    comentarios='Departamento de Cirugía',
                    activo=True
                )

                ua_urgencias = Lugares.objects.create(
                    nombre='Urgencias',
                    padre=ue_hospital,
                    tipo_nivel=tipos[2],
                    comentarios='Servicio de Urgencias 24/7',
                    activo=True
                )

                ua_consulta = Lugares.objects.create(
                    nombre='Consulta Externa',
                    padre=ue_centro,
                    tipo_nivel=tipos[2],
                    comentarios='Consultorios de Atención Ambulatoria',
                    activo=True
                )

                self.stdout.write(self.style.SUCCESS(
                    f'✓ Creadas {Lugares.objects.filter(nivel=2).count()} '
                    'Unidades Asistenciales'
                ))

                # NIVEL 3: Servicios
                serv_pabellon = Lugares.objects.create(
                    nombre='Pabellón Quirúrgico',
                    padre=ua_cirugia,
                    tipo_nivel=tipos[3],
                    comentarios='Salas de Operaciones',
                    activo=True
                )

                serv_triaje = Lugares.objects.create(
                    nombre='Triaje',
                    padre=ua_urgencias,
                    tipo_nivel=tipos[3],
                    comentarios='Clasificación de Pacientes',
                    activo=True
                )

                serv_medicina = Lugares.objects.create(
                    codigo='MED-GEN',
                    nombre='Medicina General',
                    padre=ua_consulta,
                    tipo_nivel=tipos[3],
                    comentarios='Consultas de Medicina General',
                    activo=True
                )

                self.stdout.write(self.style.SUCCESS(
                    f'✓ Creados {Lugares.objects.filter(nivel=3).count()} '
                    'Servicios'
                ))

                # NIVEL 4: Áreas
                area_pab1 = Lugares.objects.create(
                    nombre='Pabellón 1',
                    padre=serv_pabellon,
                    tipo_nivel=tipos[4],
                    comentarios='Primer pabellón quirúrgico',
                    activo=True
                )

                area_pab2 = Lugares.objects.create(
                    nombre='Pabellón 2',
                    padre=serv_pabellon,
                    tipo_nivel=tipos[4],
                    comentarios='Segundo pabellón quirúrgico',
                    activo=True
                )

                area_boxes = Lugares.objects.create(
                    nombre='Boxes de Atención',
                    padre=serv_triaje,
                    tipo_nivel=tipos[4],
                    comentarios='Boxes de evaluación inicial',
                    activo=True
                )

                self.stdout.write(self.style.SUCCESS(
                    f'✓ Creadas {Lugares.objects.filter(nivel=4).count()} '
                    'Áreas'
                ))

                # NIVEL 5: Sectores
                sector_preop = Lugares.objects.create(
                    nombre='Pre-Operatorio',
                    padre=area_pab1,
                    tipo_nivel=tipos[5],
                    comentarios='Preparación pre-quirúrgica',
                    activo=True
                )

                sector_quirofano = Lugares.objects.create(
                    nombre='Quirófano',
                    padre=area_pab1,
                    tipo_nivel=tipos[5],
                    comentarios='Sala de operaciones',
                    activo=True
                )

                sector_recuperacion = Lugares.objects.create(
                    nombre='Recuperación',
                    padre=area_pab2,
                    tipo_nivel=tipos[5],
                    comentarios='Post-operatorio inmediato',
                    activo=True
                )

                self.stdout.write(self.style.SUCCESS(
                    f'✓ Creados {Lugares.objects.filter(nivel=5).count()} '
                    'Sectores'
                ))

                # NIVEL 6: Ubicaciones
                ubic_sala1 = Lugares.objects.create(
                    nombre='Sala 1',
                    padre=sector_quirofano,
                    tipo_nivel=tipos[6],
                    comentarios='Primera sala de operaciones',
                    activo=True
                )

                ubic_sala2 = Lugares.objects.create(
                    nombre='Sala 2',
                    padre=sector_quirofano,
                    tipo_nivel=tipos[6],
                    comentarios='Segunda sala de operaciones',
                    activo=True
                )

                self.stdout.write(self.style.SUCCESS(
                    f'✓ Creadas {Lugares.objects.filter(nivel=6).count()} '
                    'Ubicaciones'
                ))

                # NIVEL 7: Puestos
                puesto_anestesia = Lugares.objects.create(
                    codigo='ANES-01',
                    nombre='Estación de Anestesia',
                    padre=ubic_sala1,
                    tipo_nivel=tipos[7],
                    comentarios='Puesto del anestesiólogo',
                    activo=True
                )

                puesto_instrumental = Lugares.objects.create(
                    codigo='INST-01',
                    nombre='Mesa de Instrumental',
                    padre=ubic_sala1,
                    tipo_nivel=tipos[7],
                    comentarios='Puesto de instrumentación',
                    activo=True
                )

                puesto_cirugia = Lugares.objects.create(
                    codigo='CIR-01',
                    nombre='Mesa Quirúrgica',
                    padre=ubic_sala1,
                    tipo_nivel=tipos[7],
                    comentarios='Mesa de cirugía principal',
                    activo=True
                )

                self.stdout.write(self.style.SUCCESS(
                    f'✓ Creados {Lugares.objects.filter(nivel=7).count()} '
                    'Puestos'
                ))

                # Resumen final
                total = Lugares.objects.count()
                self.stdout.write(self.style.SUCCESS(
                    f'\n✅ Estructura jerárquica creada exitosamente!'
                ))
                self.stdout.write(self.style.SUCCESS(
                    f'   Total: {total} lugares en 7 niveles'
                ))

                # Mostrar algunas rutas de ejemplo
                self.stdout.write(self.style.WARNING(
                    '\n📍 Rutas jerárquicas de ejemplo:'
                ))

                ejemplos = [
                    puesto_cirugia,
                    puesto_anestesia,
                    sector_recuperacion,
                    serv_medicina,
                ]

                for lugar in ejemplos:
                    self.stdout.write(
                        f'   • {lugar.nombre_completo}'
                    )

        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'\n❌ Error: {str(e)}'
            ))
            raise
