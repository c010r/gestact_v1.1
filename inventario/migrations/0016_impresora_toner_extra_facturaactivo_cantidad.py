from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0015_plantilladispositivo_fecha_adquisicion'),
    ]

    operations = [
        migrations.AddField(
            model_name='impresora',
            name='cantidad_toner_extra',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Unidades de tóner que se entregan junto a la impresora cuando se emite un remito.',
                verbose_name='Cantidad de tóner extra',
            ),
        ),
        migrations.AddField(
            model_name='impresora',
            name='insumo_toner_extra',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='impresoras_con_toner_extra',
                to='inventario.insumo',
                verbose_name='Tóner extra asociado',
            ),
        ),
        migrations.AddField(
            model_name='impresora',
            name='requiere_toner_extra',
            field=models.BooleanField(
                default=False,
                help_text='Indica si esta impresora debe enviarse con un cartucho de tóner adicional.',
                verbose_name='Suministrar tóner extra',
            ),
        ),
        migrations.AddField(
            model_name='facturaactivo',
            name='cantidad',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='facturaactivo',
            name='tipo_activo',
            field=models.CharField(
                choices=[
                    ('computadora', 'Computadora'),
                    ('impresora', 'Impresora'),
                    ('monitor', 'Monitor'),
                    ('insumo', 'Insumo'),
                ],
                max_length=20,
            ),
        ),
    ]
