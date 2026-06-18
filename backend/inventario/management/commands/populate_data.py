from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.hashers import make_password

from inventario.models import Mercado
from usuarios.models import Usuario
from proveedores.models import Proveedor


MERCADOS = [
    {
        "nombre": "Minimarket Centro",
        "ruc": "10472583961",
        "direccion": "Av. Primavera 245, Centro",
        "telefono": "987654321",
    },
    {
        "nombre": "Minimarket Norte",
        "ruc": "10918273645",
        "direccion": "Av. Los Olivos 780, Zona Norte",
        "telefono": "987654322",
    },
]

USUARIOS = [
    {
        "username": "admin",
        "password": "admin123",
        "email": "admin@minimarket.com",
        "first_name": "Admin",
        "last_name": "Principal",
        "rol": "ADMIN",
        "mercado_nombre": "Minimarket Centro",
        "is_staff": True,
        "is_superuser": True,
    },
    {
        "username": "admincentro",
        "password": "admin123",
        "email": "admincentro@minimarket.com",
        "first_name": "Admin",
        "last_name": "Centro",
        "rol": "ADMIN",
        "mercado_nombre": "Minimarket Centro",
        "is_staff": True,
        "is_superuser": False,
    },
    {
        "username": "adminnorte",
        "password": "admin123",
        "email": "adminnorte@minimarket.com",
        "first_name": "Admin",
        "last_name": "Norte",
        "rol": "ADMIN",
        "mercado_nombre": "Minimarket Norte",
        "is_staff": True,
        "is_superuser": False,
    },
    {
        "username": "vendedor1",
        "password": "vendedor123",
        "email": "vendedor1@minimarket.com",
        "first_name": "Vendedor",
        "last_name": "Centro",
        "rol": "VENDEDOR",
        "mercado_nombre": "Minimarket Centro",
        "is_staff": False,
        "is_superuser": False,
    },
    {
        "username": "vendedor2",
        "password": "vendedor123",
        "email": "vendedor2@minimarket.com",
        "first_name": "Vendedor",
        "last_name": "Norte",
        "rol": "VENDEDOR",
        "mercado_nombre": "Minimarket Norte",
        "is_staff": False,
        "is_superuser": False,
    },
]

PROVEEDORES = [
    {
        "nombre": "Distribuidora San Jorge",
        "ruc": "20123456789",
        "telefono": "998877665",
        "direccion": "Av. Industrial 500, Lima",
        "email": "ventas@sanJorge.com",
    },
    {
        "nombre": "Grupo Alimenta SAC",
        "ruc": "20234567890",
        "telefono": "997766554",
        "direccion": "Jr. Comercio 320, Lima",
        "email": "contacto@alimenta.com",
    },
    {
        "nombre": "Corporación Bebidas Perú",
        "ruc": "20345678901",
        "telefono": "996655443",
        "direccion": "Calle Las Palmeras 150, Callao",
        "email": "pedidos@bebidasperu.com",
    },
    {
        "nombre": "Lácteos del Valle EIRL",
        "ruc": "20456789012",
        "telefono": "995544332",
        "direccion": "Carretera Central Km 15, Huachipa",
        "email": "info@lacteosdelvalle.com",
    },
    {
        "nombre": "Distribuidora de Abarrotes El Mayorista",
        "ruc": "20567890123",
        "telefono": "994433221",
        "direccion": "Av. Grau 800, Lima",
        "email": "ventas@elmayorista.com",
    },
]


class Command(BaseCommand):
    help = "Pobla datos iniciales de Mercados, Usuarios y Proveedores."

    def handle(self, *args, **options):
        self._populate_mercados()
        self._populate_usuarios()
        self._populate_proveedores()

    def _populate_mercados(self):
        created = 0
        for data in MERCADOS:
            _, was_created = Mercado.objects.get_or_create(
                nombre=data["nombre"],
                defaults={
                    "ruc": data["ruc"],
                    "direccion": data["direccion"],
                    "telefono": data["telefono"],
                },
            )
            if was_created:
                created += 1
                self.stdout.write(f"  [CREADO] Mercado: {data['nombre']}")
            else:
                self.stdout.write(f"  [EXISTE] Mercado: {data['nombre']}")
        self.stdout.write(self.style.SUCCESS(f"Mercados: {created} creado(s)"))

    def _populate_usuarios(self):
        mercados = {m.nombre: m for m in Mercado.objects.all()}
        created = updated = 0
        for data in USUARIOS:
            mercado = mercados.get(data["mercado_nombre"]) if data["mercado_nombre"] else None
            defaults = {
                "password": make_password(data["password"]),
                "email": data["email"],
                "first_name": data["first_name"],
                "last_name": data["last_name"],
                "rol": data["rol"],
                "mercado": mercado,
                "is_staff": data["is_staff"],
                "is_superuser": data["is_superuser"],
            }
            usuario, was_created = Usuario.objects.get_or_create(
                username=data["username"],
                defaults=defaults,
            )
            if was_created:
                created += 1
                self.stdout.write(f"  [CREADO] Usuario: {data['username']}")
            else:
                changed = False
                for field, value in defaults.items():
                    if field == "password":
                        if not usuario.check_password(data["password"]):
                            usuario.set_password(data["password"])
                            changed = True
                    elif getattr(usuario, field) != value:
                        setattr(usuario, field, value)
                        changed = True
                if changed:
                    usuario.save()
                    updated += 1
                    self.stdout.write(f"  [ACTUALIZADO] Usuario: {data['username']}")
                else:
                    self.stdout.write(f"  [EXISTE] Usuario: {data['username']}")
        self.stdout.write(self.style.SUCCESS(f"Usuarios: {created} creado(s), {updated} actualizado(s)"))

    def _populate_proveedores(self):
        created = 0
        for data in PROVEEDORES:
            _, was_created = Proveedor.objects.get_or_create(
                nombre=data["nombre"],
                defaults={
                    "ruc": data["ruc"],
                    "telefono": data["telefono"],
                    "direccion": data["direccion"],
                    "email": data["email"],
                },
            )
            if was_created:
                created += 1
                self.stdout.write(f"  [CREADO] Proveedor: {data['nombre']}")
            else:
                self.stdout.write(f"  [EXISTE] Proveedor: {data['nombre']}")
        self.stdout.write(self.style.SUCCESS(f"Proveedores: {created} creado(s)"))
