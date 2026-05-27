from django.contrib import admin
from .models import Cliente, Producto, Venta, DetalleVenta, Caja, MovimientoCaja

admin.site.register(Cliente)
admin.site.register(Producto)
admin.site.register(Venta)
admin.site.register(DetalleVenta)
admin.site.register(Caja)
admin.site.register(MovimientoCaja)