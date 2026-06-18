from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, connection
from django.core.cache import cache

from inventario.models import Kardex, UnidadProducto, Producto, Categoria
from ventas.models import Venta, Caja, Cliente
from compras.models import Compra
from inventario.models import Transferencia
from usuarios.models import Usuario
from inventario.models import Mercado
from proveedores.models import Proveedor


MODELS_TO_DELETE = [
    Kardex,
    UnidadProducto,
    Venta,
    Caja,
    Compra,
    Transferencia,
    Producto,
    Categoria,
    Cliente,
]

MODELS_TO_KEEP = [
    Usuario,
    Mercado,
    Proveedor,
]


class Command(BaseCommand):
    help = 'Elimina todos los datos del sistema excepto Usuarios, Mercados y Proveedores.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-input', action='store_true', dest='no_input',
            help='Ejecutar sin confirmación interactiva.',
        )

    def handle(self, *args, **options):
        no_input = options.get('no_input', False)

        if not self._check_database():
            raise CommandError('Este comando solo funciona con MySQL.')

        counts = self._get_counts()

        self.stdout.write(self.style.WARNING('=' * 60))
        self.stdout.write(self.style.WARNING('RESET DE DATOS DEL SISTEMA'))
        self.stdout.write(self.style.WARNING('=' * 60))
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('Se ELIMINARÁN los siguientes datos:'))
        self.stdout.write('')
        for model, count in counts.items():
            name = model._meta.verbose_name_plural.capitalize()
            self.stdout.write(f'  - {name}: {count} registro(s)')
        self.stdout.write('')
        kept_names = [m._meta.verbose_name_plural.capitalize() for m in MODELS_TO_KEEP]
        self.stdout.write(self.style.SUCCESS(f'Se CONSERVARÁN: {", ".join(kept_names)}'))
        self.stdout.write('')

        if not no_input:
            confirm = input('¿Está seguro de que desea eliminar todos estos datos? (s/N): ')
            if confirm.lower() != 's':
                self.stdout.write(self.style.WARNING('Operación cancelada.'))
                return

        self._delete_data()
        self._reset_auto_increment()
        self._invalidate_cache()

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Datos eliminados correctamente.'))
        self.stdout.write(self.style.SUCCESS('  - Usuarios, Mercados y Proveedores conservados.'))
        self.stdout.write(self.style.SUCCESS('  - Cache del sistema invalidada.'))
        self.stdout.write('')

    def _check_database(self):
        engine = connection.vendor
        return engine == 'mysql'

    def _get_table_model_map(self):
        return {model._meta.db_table: model for model in MODELS_TO_DELETE}

    def _get_counts(self):
        counts = {}
        for model in MODELS_TO_DELETE:
            counts[model] = model.objects.count()
        return counts

    def _delete_data(self):
        self.stdout.write('')
        self.stdout.write('Eliminando datos...')

        deleted_counts = {}

        deleted_counts['Kardex'] = self._delete_model(Kardex)
        deleted_counts['UnidadProducto'] = self._delete_model(UnidadProducto)

        venta_count = Venta.objects.count()
        with transaction.atomic():
            Venta.objects.all().delete()
        deleted_counts['Venta'] = venta_count

        deleted_counts['Caja'] = self._delete_model(Caja)
        deleted_counts['Compra'] = self._delete_model(Compra)
        deleted_counts['Transferencia'] = self._delete_model(Transferencia)
        deleted_counts['Producto'] = self._delete_model(Producto)
        deleted_counts['Categoria'] = self._delete_model(Categoria)
        deleted_counts['Cliente'] = self._delete_model(Cliente)

        self.stdout.write('')
        for name, count in deleted_counts.items():
            self.stdout.write(f'  {name}: {count} eliminado(s)')

    def _delete_model(self, model):
        count = model.objects.count()
        if count == 0:
            return 0
        with transaction.atomic():
            model.objects.all().delete()
        return count

    def _reset_auto_increment(self):
        self.stdout.write('')
        self.stdout.write('Reseteando secuencias AUTO_INCREMENT...')

        tables = [m._meta.db_table for m in MODELS_TO_DELETE]

        with connection.cursor() as cursor:
            for table in tables:
                try:
                    cursor.execute(f"ALTER TABLE `{table}` AUTO_INCREMENT = 1;")
                    self.stdout.write(f'  [OK] {table}')
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'  [WARN] {table}: {e}'))

    def _invalidate_cache(self):
        cache.clear()
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('  Cache global limpiada.'))
