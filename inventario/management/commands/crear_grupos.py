"""
Management command: crear_grupos
Crea (o actualiza) los 4 grupos de acceso del sistema ASSE-GestACT.

Uso:
    python manage.py crear_grupos
    python manage.py crear_grupos --resetear     # elimina y recrea todos los grupos
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


GRUPOS = [
    {
        'nombre': 'Activos Informáticos',
        'descripcion': 'Acceso al módulo de gestión de activos informáticos (TI): '
                       'computadoras, impresoras, monitores, networking, telefonía, '
                       'periféricos, software e insumos.',
    },
    {
        'nombre': 'Tecnología Médica',
        'descripcion': 'Acceso al módulo de gestión de equipos de tecnología médica.',
    },
    {
        'nombre': 'Activos Generales',
        'descripcion': 'Acceso al módulo de gestión de activos generales: '
                       'mobiliario, vehículos y herramientas.',
    },
    {
        'nombre': 'Administrador',
        'descripcion': 'Acceso completo a todos los módulos del sistema: '
                       'Activos Informáticos, Tecnología Médica y Activos Generales. '
                       'También tiene acceso a reportes y configuración.',
    },
]


class Command(BaseCommand):
    help = 'Crea los 4 grupos de acceso del sistema ASSE-GestACT'

    def add_arguments(self, parser):
        parser.add_argument(
            '--resetear',
            action='store_true',
            help='Elimina y recrea todos los grupos (útil para limpiar permisos)',
        )

    def handle(self, *args, **options):
        resetear = options['resetear']

        if resetear:
            self.stdout.write(self.style.WARNING('Eliminando grupos existentes...'))
            for grupo_data in GRUPOS:
                deleted, _ = Group.objects.filter(name=grupo_data['nombre']).delete()
                if deleted:
                    self.stdout.write(f"  Eliminado: {grupo_data['nombre']}")

        self.stdout.write(self.style.MIGRATE_HEADING('\nCreando grupos de acceso:'))

        creados = 0
        existentes = 0

        for grupo_data in GRUPOS:
            grupo, created = Group.objects.get_or_create(name=grupo_data['nombre'])
            if created:
                creados += 1
                self.stdout.write(
                    self.style.SUCCESS(f"  [OK] Creado:   {grupo.name}")
                )
            else:
                existentes += 1
                self.stdout.write(
                    self.style.WARNING(f"  ~ Existente: {grupo.name}")
                )

        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(
                f'Resumen: {creados} grupo(s) creado(s), {existentes} ya existían.'
            )
        )

        self.stdout.write('')
        self.stdout.write(self.style.MIGRATE_HEADING('Grupos disponibles y su acceso:'))
        for grupo_data in GRUPOS:
            self.stdout.write(f"\n  [{grupo_data['nombre']}]")
            self.stdout.write(f"    {grupo_data['descripcion']}")

        self.stdout.write('')
        self.stdout.write(
            'Para asignar un grupo a un usuario, usa la shell de Django:\n'
            '  python manage.py shell\n'
            '  >>> from django.contrib.auth.models import User, Group\n'
            '  >>> u = User.objects.get(username="mi_usuario")\n'
            '  >>> g = Group.objects.get(name="Administrador")\n'
            '  >>> u.groups.add(g)\n'
        )
