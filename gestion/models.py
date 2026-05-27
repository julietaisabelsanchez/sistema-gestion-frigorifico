from django.db import models

# =========================
# 👥 CLIENTES
# =========================
class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    direccion = models.CharField(max_length=255)
    dni = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.nombre


# =========================
# 📦 PRODUCTOS
# =========================
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50)
    precio = models.FloatField()
    stock = models.IntegerField()

    def __str__(self):
        return self.nombre


# =========================
# 👨‍💼 EMPLEADOS
# =========================
class Empleado(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    puesto = models.CharField(max_length=50)
    salario = models.FloatField()
    dias_trabajo = models.CharField(max_length=100)
    horario = models.CharField(max_length=100)
    fecha_ingreso = models.DateField(auto_now_add=True)
    foto = models.ImageField(upload_to='empleados/', blank=True, null=True)

    def __str__(self):
        return self.nombre


# =========================
# 💰 VENTAS
# =========================
class Venta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha = models.DateField()
    numero_comprobante = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Venta {self.numero_comprobante} - {self.cliente.nombre}"
    
class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    subtotal = models.FloatField()

    def __str__(self):
        return f"{self.producto} x {self.cantidad}"


# =========================
# 💳 PAGOS
# =========================
class Pago(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    monto = models.FloatField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pago ${self.monto}"


# =========================
# 🧾 FACTURAS
# =========================
class Factura(models.Model):
    numero = models.AutoField(primary_key=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.FloatField()

    def __str__(self):
        return f"Factura {self.numero}"


class DetalleFactura(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio = models.FloatField()

    def __str__(self):
        return f"{self.producto} x {self.cantidad}"


# =========================
# 💰 CAJA
# =========================
class Caja(models.Model):
    fecha = models.DateField(auto_now_add=True)
    apertura = models.FloatField(default=0)
    ingresos = models.FloatField(default=0)
    egresos = models.FloatField(default=0)
    cierre = models.FloatField(default=0)

    def __str__(self):
        return f"Caja {self.fecha}"


class MovimientoCaja(models.Model):
    caja = models.ForeignKey(Caja, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10)
    monto = models.FloatField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo} - ${self.monto}"


# =========================
# 🚚 ENVIOS
# =========================
class Envio(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    direccion = models.CharField(max_length=200)
    ciudad = models.CharField(max_length=100)
    estado = models.CharField(max_length=20, default='Pendiente')
    fecha = models.DateTimeField(auto_now_add=True)
    observacion = models.TextField(blank=True, null=True)
    latitud = models.FloatField(null=True, blank=True)
    longitud = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Envio {self.id} - {self.cliente}"


# =========================
# 📒 CUENTA CORRIENTE
# =========================
class CuentaCorriente(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha = models.DateField(auto_now_add=True)
    descripcion = models.CharField(max_length=200, default="Venta")
    cajas = models.IntegerField(default=0)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pago = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.total = self.cajas * self.precio_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cliente} - {self.fecha}"