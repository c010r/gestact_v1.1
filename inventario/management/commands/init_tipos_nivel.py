"""
Comando de gestión para inicializar los tipos de nivel jerárquico
"""
from django.core.management.base import BaseCommand
from inventario.models import TipoNivel


class Command(BaseCommand):
    help = 'Inicializa los tipos de nivel jerárquico predeterminados'

    def handle(self, *args, **options):
        """Crear los tipos de nivel predeterminados"""

        tipos_nivel = [
            {
                'nombre': 'Unidad Ejecutora',
                'nivel': 1,
                'descripcion': (
                    'Primer nivel jerárquico - Unidad ejecutora principal'
                ),
                'requiere_codigo': True,
                'activo': True
            },
            {
                'nombre': 'Unidad Asistencial',
                'nivel': 2,
                'descripcion': (
                    'Segundo nivel - Unidad asistencial o departamento'
                ),
                'requiere_codigo': False,
                'activo': True
            },
            {
                'nombre': 'Servicio',
                'nivel': 3,
                'descripcion': 'Tercer nivel - Servicio específico',
                'requiere_codigo': False,
                'activo': True
            },
            {
                'nombre': 'Área',
                'nivel': 4,
                'descripcion': 'Cuarto nivel - Área o sección',
                'requiere_codigo': False,
                'activo': True
            },
            {
                'nombre': 'Sector',
                'nivel': 5,
                'descripcion': 'Quinto nivel - Sector o zona',
                'requiere_codigo': False,
                'activo': True
            },
            {
                'nombre': 'Ubicación',
                'nivel': 6,
                'descripcion': 'Sexto nivel - Ubicación específica',
                'requiere_codigo': False,
                'activo': True
            },
            {
                'nombre': 'Puesto',
                'nivel': 7,
                'descripcion': (
                    'Séptimo nivel - Puesto o lugar físico específico'
                ),
                'requiere_codigo': False,
                'activo': True
            },
        ]

        creados = 0
        actualizados = 0

        for tipo_data in tipos_nivel:
            tipo, created = TipoNivel.objects.update_or_create(
                nombre=tipo_data['nombre'],
                nivel=tipo_data['nivel'],
                defaults={
                    'descripcion': tipo_data['descripcion'],
                    'requiere_codigo': tipo_data['requiere_codigo'],
                    'activo': tipo_data['activo']
                }
            )

            if created:
                creados += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Creado: Nivel {tipo.nivel} - {tipo.nombre}'
                    )
                )
            else:
                actualizados += 1
                self.stdout.write(
                    self.style.WARNING(
                        f'↻ Actualizado: Nivel {tipo.nivel} - {tipo.nombre}'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Proceso completado: {creados} creados, '
                f'{actualizados} actualizados'
            )
        )
