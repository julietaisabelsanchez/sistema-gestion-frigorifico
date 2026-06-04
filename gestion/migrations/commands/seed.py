from django.core.management.base import BaseCommand
from gestion.models import Cliente, Producto, Venta
import random

class Command(BaseCommand):
    help = 'Cargar datos de prueba'

    def handle(self, *args, **kwargs):
        clientes = []
        for i in range(5):
            c = Cliente.objects.create(
                nombre=f"Cliente {i+1}",
                dni=str(2000+i)
            )
            clientes.append(c)

        productos = []
        for i in range(5):
            p = Producto.objects.create(
                nombre=f"Producto {i+1}",
                precio=random.randint(100, 500),
                stock=100
            )
            productos.append(p)

        for i in range(20):
            Venta.objects.create(
                cliente=random.choice(clientes),
                producto=random.choice(productos),
                cantidad=random.randint(1, 5)
            )

        self.stdout.write(self.style.SUCCESS('🔥 Datos cargados'))