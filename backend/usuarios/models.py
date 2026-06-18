from django.db import models
from django.contrib.auth.models import AbstractUser
from inventario.models import Mercado

class Usuario(AbstractUser):
    ROLES = (
        ('ADMIN', 'Administrador'),
        ('VENDEDOR', 'Vendedor'),
    )
    rol = models.CharField(max_length=20, choices=ROLES, default='VENDEDOR')
    mercado = models.ForeignKey(Mercado, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def is_admin(self):
        return self.rol == 'ADMIN'

    @property
    def is_vendedor(self):
        return self.rol == 'VENDEDOR'