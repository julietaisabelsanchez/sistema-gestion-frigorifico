import json
import os
from decimal import Decimal
from datetime import date, datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from django.conf import settings

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors



from django.shortcuts import render
from django.http import HttpResponse
from .models import CuentaCorriente, Cliente
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from django.shortcuts import render
from .models import Venta, Cliente
from django.shortcuts import render
from .models import Venta, Cliente
from django.shortcuts import render
from .models import Venta, Cliente
from reportlab.pdfgen import canvas
from django.http import HttpResponse
import os
import json
from pathlib import Path
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import (
    Cliente,
    Producto,
    Venta,
    DetalleVenta,
    Pago,
    Caja,
    MovimientoCaja,
    Empleado,
    Envio,
    CuentaCorriente
)

from .forms import (
    EmpleadoForm,
    VentaForm,
    CuentaCorrienteForm
)


# =========================
# 🔐 LOGIN
# =========================
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user:
            login(request, user)
            return redirect("/")
        else:
            return render(
                request,
                "login.html",
                {"error": "Usuario o contraseña incorrectos"}
            )

    return render(request, "login.html")
# =========================
# 📊 DASHBOARD
# =========================
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect("/login/")

    return render(request, 'dashboard.html')


# =========================
# 📦 PRODUCTOS
# =========================
def productos(request):
    query = request.GET.get("q")
    productos = Producto.objects.filter(nombre__icontains=query) if query else Producto.objects.all()
    return render(request, "productos.html", {"productos": productos})


def agregar_producto(request):
    if request.method == 'POST':
        Producto.objects.create(
            nombre=request.POST.get('nombre'),
            precio=request.POST.get('precio'),
            stock=request.POST.get('stock')
        )
        return redirect('productos')

    return render(request, 'agregar_producto.html')



# 📦 STOCK
# =========================
def stock_grasas_cajas(request):
    productos = Producto.objects.filter(nombre__icontains="grasa") | Producto.objects.filter(nombre__icontains="caja")
    return render(request, "stock_grasas_cajas.html", {"productos": productos})


# =========================
# 👥 CLIENTES
# =========================
def clientes(request):
    return render(request, 'clientes.html', {
        'clientes': Cliente.objects.all()
    })


def agregar_cliente(request):
    if request.method == 'POST':
        Cliente.objects.create(
            nombre=request.POST.get('nombre'),
            telefono=request.POST.get('telefono') or "",
            dni=request.POST.get('dni'),
            direccion=request.POST.get('direccion') or ""
        )
        return redirect('clientes')

    return render(request, 'agregar_cliente.html')


def editar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)

    if request.method == 'POST':
        cliente.nombre = request.POST.get('nombre')
        cliente.telefono = request.POST.get('telefono')
        cliente.dni = request.POST.get('dni')
        cliente.direccion = request.POST.get('direccion')
        cliente.save()
        return redirect('clientes')

    return render(request, 'editar_cliente.html', {'cliente': cliente})


def eliminar_cliente(request, id):
    Cliente.objects.get(id=id).delete()
    return redirect('clientes')


# =========================
# 💰 VENTAS
# =========================
def ventas(request):
    clientes = Cliente.objects.all()
    productos = Producto.objects.all()

    if request.method == 'POST':
        cliente_id = request.POST.get('cliente')
        producto_id = request.POST.get('producto')
        cantidad = int(request.POST.get('cantidad', 0))

        if cliente_id and producto_id and cantidad > 0:
            cliente = Cliente.objects.get(pk=cliente_id)
            producto = Producto.objects.get(pk=producto_id)

            if producto.stock >= cantidad:
                producto.stock -= cantidad
                producto.save()

                venta = Venta.objects.create(
                    cliente=cliente,
                    fecha=date.today(),
                    numero_comprobante=f"F-{Venta.objects.count() + 1:05d}"
                )

                DetalleVenta.objects.create(
                    venta=venta,
                    producto=producto,
                    cantidad=cantidad,
                    subtotal=producto.precio * cantidad
                )

                return redirect('ventas')

    ventas = Venta.objects.order_by('-fecha')

    return render(request, 'ventas.html', {
        'clientes': clientes,
        'productos': productos,
        'ventas': ventas
    })
# =========================
# 👨‍💼 EMPLEADOS
# =========================
def empleados(request):
    return render(request, 'empleados.html', {
        'empleados': Empleado.objects.all()
    })


def agregar_empleado(request):
    if request.method == 'POST':

        nombre = request.POST.get('nombre')
        telefono = request.POST.get('telefono')
        salario = request.POST.get('salario') or 0

        Empleado.objects.create(
            nombre=nombre,
            telefono=telefono,
            salario=salario
        )

        return redirect('empleados')

    return render(request, 'agregar_empleado.html')


def editar_empleado(request, id):
    empleado = get_object_or_404(Empleado, id=id)

    if request.method == 'POST':
        empleado.nombre = request.POST.get('nombre')
        empleado.telefono = request.POST.get('telefono')
        empleado.save()
        return redirect('empleados')

    return render(request, 'editar_empleado.html', {'empleado': empleado})


def eliminar_empleado(request, id):
    Empleado.objects.get(id=id).delete()
    return redirect('empleados')

# =========================
# 🚚 ENVIOS
# =========================
def envios(request):
    clientes = Cliente.objects.all()

    if request.method == 'POST':
        cliente_id = request.POST.get('cliente')
        direccion = request.POST.get('direccion')
        ciudad = request.POST.get('ciudad')

        print("POST:", request.POST)

        if cliente_id and direccion and ciudad:
            cliente = Cliente.objects.get(pk=cliente_id)

            Envio.objects.create(
                cliente=cliente,
                direccion=direccion,
                ciudad=ciudad,
                estado='Pendiente'
            )

            return redirect('envios')

    envios = Envio.objects.exclude(estado='Entregado')

    return render(request, 'envios.html', {
        'clientes': clientes,
        'envios': envios
    })


def cambiar_estado_envio(request, id):
    envio = get_object_or_404(Envio, id=id)

    if envio.estado == "Pendiente":
        envio.estado = "En camino"
    elif envio.estado == "En camino":
        envio.estado = "Entregado"
    else:
        envio.estado = "Pendiente"

    envio.save()
    return redirect('envios')
# =========================
# 💰 CAJA
# =========================
def factura_pdf(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    detalles = DetalleVenta.objects.filter(venta=venta)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="factura_{venta.id}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # LOGO
    logo_path = os.path.join(settings.BASE_DIR, 'gestion', 'static', 'logo.png')
    if os.path.exists(logo_path):
        p.drawImage(logo_path, 40, height - 130, width=90, height=90)

    # TITULO
    p.setFont("Helvetica-Bold", 18)
    p.drawString(160, height - 60, "ENTE FRIGORIFICO CHICOANA")

    p.setFont("Helvetica", 11)
    p.drawString(160, height - 85, f"Cliente: {venta.cliente.nombre}")
    p.drawString(160, height - 105, f"Fecha: {venta.fecha}")
    p.drawString(160, height - 125, f"N° Comprobante: {venta.numero_comprobante}")

    # TABLA
    y = height - 200

    p.setFillColor(colors.black)
    p.rect(40, y, 520, 30, fill=1)

    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 11)
    p.drawString(60, y + 10, "Producto")
    p.drawString(350, y + 10, "Cantidad")
    p.drawString(450, y + 10, "Total")

    total_general = 0
    y -= 30

    for detalle in detalles:
        p.setFillColor(colors.black)
        p.rect(40, y, 520, 30, fill=0)

        p.setFont("Helvetica", 10)
        p.drawString(60, y + 10, detalle.producto.nombre)
        p.drawString(370, y + 10, str(detalle.cantidad))

        subtotal = int(detalle.subtotal)
        total_general += subtotal

        total_formateado = f"${subtotal:,.0f}".replace(",", ".")
        p.drawString(450, y + 10, total_formateado)

        y -= 30

    # TOTAL FINAL
    y -= 30
    p.setFont("Helvetica-Bold", 16)
    total_final = f"${total_general:,.0f}".replace(",", ".")
    p.drawString(380, y, f"TOTAL: {total_final}")

    p.showPage()
    p.save()

    return response

def caja_pdf(request):
    return HttpResponse("PDF")


def caja(request):
    hoy = now().date()

    caja, _ = Caja.objects.get_or_create(fecha=hoy)

    fecha = request.GET.get('fecha')
    if fecha:
        movimientos = MovimientoCaja.objects.filter(fecha=fecha)
    else:
        movimientos = MovimientoCaja.objects.filter(fecha=hoy)

    if request.method == 'POST':
        try:
            monto = Decimal(request.POST.get('monto', '0'))
            tipo = request.POST.get('tipo')

            MovimientoCaja.objects.create(
                caja=caja,
                tipo=tipo,
                monto=float(monto)
            )

            if tipo == "apertura":
                caja.apertura += float(monto)
            elif tipo == "ingreso":
                caja.ingresos += float(monto)
            elif tipo == "egreso":
                caja.egresos += float(monto)

            caja.save()

        except Exception as e:
            print("ERROR CAJA:", e)

        return redirect('caja')

    saldo = (caja.apertura or 0) + (caja.ingresos or 0) - (caja.egresos or 0)
    ganancias = (caja.ingresos or 0) - (caja.egresos or 0)

    return render(request, "caja.html", {
        "caja": caja,
        "movimientos": movimientos,
        "saldo": saldo,
        "ganancias": ganancias,
        "fecha": fecha or hoy
    })

def datos_dashboard(request):

    productos_bajo = Producto.objects.filter(stock__lt=10)

    ventas_recientes = Venta.objects.order_by('-fecha')[:5]

    fechas = []
    totales = []

    for venta in ventas_recientes:
        fechas.append(venta.fecha.strftime('%d/%m'))
        total_venta = venta.detalleventa_set.aggregate
        total=Sum('subtotal')

    # 💰 TOTAL VENTAS
    total_ventas = Venta.objects.aggregate(
        Sum('detalleventa__subtotal')
    )['total__sum'] or 0

    # 💳 TOTAL PAGADO
    total_pagado_ventas = Venta.objects.aggregate(
        Sum('monto_pagado')
    )['monto_pagado__sum'] or 0

    pagos_extra = Pago.objects.aggregate(
        Sum('monto')
    )['monto__sum'] or 0

    total_pagado = total_pagado_ventas + pagos_extra

    # 📉 DEUDA TOTAL
    total_deudas = total_ventas - total_pagado

    return JsonResponse({
        'ventas': float(total_ventas),
        'productos': Producto.objects.count(),
        'clientes': Cliente.objects.count(),
        'deudas': float(total_deudas),
        'stock_bajo': productos_bajo.count(),
        'stock_nombres': [p.nombre for p in productos_bajo],
        'fechas': fechas,
        'totales': totales,
    })
def deudas(request):
    clientes = Cliente.objects.all()
    datos = []

    for cliente in clientes:
        ventas = Venta.objects.filter(cliente=cliente).aggregate(
            total=Sum('detalleventa__subtotal')
        )['total'] or 0

        pagos = Pago.objects.filter(cliente=cliente).aggregate(
            total=Sum('monto')
        )['total'] or 0

        deuda = ventas - pagos

        datos.append({
            'cliente': cliente,
            'ventas': ventas,
            'pagos': pagos,
            'deuda': deuda,
        })

    return render(request, 'deudas.html', {'datos': datos})

def registrar_pago(request, cliente_id):
    if request.method == 'POST':
        monto = float(request.POST.get('monto', 0))
        cliente = Cliente.objects.get(id=cliente_id)

        Pago.objects.create(
            cliente=cliente,
            monto=monto
        )

    return redirect('deudas')


def recibo_pago_pdf(request, cliente_id):
    cliente = Cliente.objects.get(id=cliente_id)

    try:
        monto_str = request.GET.get('monto', '0').replace(',', '.')
        monto = float(monto_str)
    except ValueError:
        monto = 0

    fecha = datetime.now().strftime("%d/%m/%Y")

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="recibo_pago.pdf"'

    p = canvas.Canvas(response)
    width, height = p._pagesize

    # LOGO
    logo_path = os.path.join(settings.BASE_DIR, 'gestion', 'static', 'logo.png')
    if os.path.exists(logo_path):
        p.drawImage(logo_path, 50, height - 140, width=90, height=90)

    # EMPRESA
    p.setFont("Helvetica-Bold", 20)
    p.drawString(170, height - 70, "ENTE FRIGORIFICO CHICOANA")

    p.setFont("Helvetica-Bold", 18)
    p.drawString(220, height - 120, "RECIBO DE COBRO")

    # DATOS
    monto_formateado = f"${monto:,.0f}".replace(",", ".")

    p.setFont("Helvetica", 13)
    p.drawString(80, height - 220, f"Cliente: {cliente.nombre}")
    p.drawString(80, height - 260, f"Fecha: {fecha}")
    p.drawString(80, height - 300, f"Monto Cobrado: {monto_formateado}")

    # FIRMAS
    p.line(80, height - 500, 250, height - 500)
    p.drawString(90, height - 525, "Firma y aclaración")
    p.drawString(105, height - 550, "del Remitente")

    p.line(350, height - 500, 520, height - 500)
    p.drawString(390, height - 530, "Sello de la Empresa")

    p.showPage()
    p.save()

    return response
def editar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)

    if request.method == 'POST':
        producto.nombre = request.POST.get('nombre')
        producto.precio = request.POST.get('precio')
        producto.stock = request.POST.get('stock')
        producto.save()
        return redirect('productos')

    return render(request, 'editar_producto.html', {'producto': producto})
def cambiar_stock(request, id):
    producto = get_object_or_404(Producto, id=id)

    if request.method == 'POST':
        producto.stock = int(request.POST.get('stock'))
        producto.save()
        return redirect('productos')

    return render(request, 'cambiar_stock.html', {'producto': producto})
def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    producto.delete()
    return redirect('productos')
def editar_venta(request, id):
    venta = get_object_or_404(Venta, id=id)
    clientes = Cliente.objects.all()
    productos = Producto.objects.all()
    detalle = DetalleVenta.objects.filter(venta=venta).first()

    if request.method == "POST":
        cliente_id = request.POST.get("cliente")
        producto_id = request.POST.get("producto")
        cantidad = request.POST.get("cantidad")
        total = request.POST.get("total")
        fecha = request.POST.get("fecha")
        comprobante = request.POST.get("comprobante")

        # cliente
        if cliente_id:
            venta.cliente = get_object_or_404(Cliente, id=cliente_id)

        # fecha
        if fecha:
            venta.fecha = fecha

        # comprobante
        venta.numero_comprobante = comprobante if comprobante else venta.numero_comprobante

        venta.save()

        if detalle:
            # devolver stock viejo
            if detalle.producto:
                detalle.producto.stock += detalle.cantidad
                detalle.producto.save()

            # producto nuevo
            if producto_id:
                nuevo_producto = get_object_or_404(Producto, id=producto_id)
                nueva_cantidad = int(cantidad) if cantidad else 0

                if nuevo_producto.stock >= nueva_cantidad:
                    nuevo_producto.stock -= nueva_cantidad
                    nuevo_producto.save()

                    detalle.producto = nuevo_producto
                    detalle.cantidad = nueva_cantidad
                    detalle.subtotal = Decimal(total) if total else Decimal("0")
                    detalle.save()

        return redirect('ventas')

    return render(request, 'editar_venta.html', {
        'venta': venta,
        'clientes': clientes,
        'productos': productos,
        'detalle': detalle
    })

def cuenta_corriente(request):
    movimientos = CuentaCorriente.objects.all().order_by('fecha')

    saldo = 0
    for mov in movimientos:
        saldo += mov.total - mov.pago
        mov.saldo = saldo

    return render(request, 'cuenta_corriente.html', {
        'movimientos': movimientos
    })


def nueva_cuenta_corriente(request):
    if request.method == 'POST':
        form = CuentaCorrienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cuenta_corriente')
    else:
        form = CuentaCorrienteForm()

    return render(request, 'form.html', {'form': form})


def eliminar_pago_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    Pago.objects.filter(cliente=cliente).delete()
    return redirect('deudas')


def editar_cuenta_corriente(request, id):
    movimiento = get_object_or_404(CuentaCorriente, id=id)

    if request.method == 'POST':
        movimiento.cliente_id = request.POST.get('cliente')
        movimiento.descripcion = request.POST.get('descripcion')
        movimiento.cajas = int(request.POST.get('cajas'))
        movimiento.precio_unitario = float(request.POST.get('precio_unitario'))
        movimiento.pago = float(request.POST.get('pago') or 0)

        movimiento.save()

        return redirect('informe_cuenta_corriente')

    clientes = Cliente.objects.all().order_by('nombre')

    return render(request, 'editar_cuenta_corriente.html', {
        'movimiento': movimiento,
        'clientes': clientes
    })


def informe_cuenta_corriente(request):
    movimientos = CuentaCorriente.objects.select_related('cliente').all().order_by('fecha')

    cliente_id = request.GET.get('cliente')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')

    if cliente_id in ["None", "", None]:
        cliente_id = None

    if fecha_desde in ["None", "", None]:
        fecha_desde = None

    if fecha_hasta in ["None", "", None]:
        fecha_hasta = None

    if cliente_id:
        movimientos = movimientos.filter(cliente_id=int(cliente_id))

    if fecha_desde:
        movimientos = movimientos.filter(fecha__gte=fecha_desde)

    if fecha_hasta:
        movimientos = movimientos.filter(fecha__lte=fecha_hasta)

    saldo_acumulado = 0
    for mov in movimientos:
        saldo_acumulado += mov.total - mov.pago
        mov.saldo = saldo_acumulado

    clientes = Cliente.objects.all().order_by('nombre')

    total_ventas = movimientos.aggregate(total=Sum('total'))['total'] or 0
    total_cobros = movimientos.aggregate(total=Sum('pago'))['total'] or 0
    saldo_final = total_ventas - total_cobros

    cliente_nombre = "Todos los clientes"

    if cliente_id:
        cliente_obj = Cliente.objects.filter(id=cliente_id).first()
        if cliente_obj:
            cliente_nombre = cliente_obj.nombre

    if movimientos.exists():
        if saldo_final > 0:
            estado = "mantiene deuda pendiente y requiere seguimiento de cobranza."
        elif saldo_final == 0:
            estado = "se encuentra al día con sus pagos."
        else:
            estado = "presenta saldo a favor."

        informe_ia = f"""
Cliente analizado: {cliente_nombre}

Durante el período seleccionado se registraron ventas por ${total_ventas},
cobros por ${total_cobros}
y un saldo pendiente de ${saldo_final}.

Análisis automático:
El cliente {estado}
"""
    else:
        informe_ia = "No se encontraron movimientos para los filtros seleccionados."

    return render(request, 'informe_cuenta_corriente.html', {
        'movimientos': movimientos,
        'clientes': clientes,
        'cliente_id': cliente_id,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'total_ventas': total_ventas,
        'total_cobros': total_cobros,
        'saldo_final': saldo_final,
        'informe_ia': informe_ia,
    })


def informe_cuenta_corriente_pdf(request):
    movimientos = CuentaCorriente.objects.select_related('cliente').all().order_by('fecha')

    cliente_id = request.GET.get('cliente')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')

    if cliente_id in ["None", "", None]:
        cliente_id = None

    if fecha_desde in ["None", "", None]:
        fecha_desde = None

    if fecha_hasta in ["None", "", None]:
        fecha_hasta = None

    if cliente_id:
        movimientos = movimientos.filter(cliente_id=int(cliente_id))

    if fecha_desde:
        movimientos = movimientos.filter(fecha__gte=fecha_desde)

    if fecha_hasta:
        movimientos = movimientos.filter(fecha__lte=fecha_hasta)

    saldo_acumulado = 0
    for mov in movimientos:
        saldo_acumulado += mov.total - mov.pago
        mov.saldo = saldo_acumulado

    total_ventas = movimientos.aggregate(total=Sum('total'))['total'] or 0
    total_cobros = movimientos.aggregate(total=Sum('pago'))['total'] or 0
    saldo_final = total_ventas - total_cobros

    cliente_nombre = "Todos los clientes"
    if cliente_id:
        cliente_obj = Cliente.objects.filter(id=cliente_id).first()
        if cliente_obj:
            cliente_nombre = cliente_obj.nombre

    if saldo_final > 0:
        estado = "mantiene deuda pendiente y requiere seguimiento."
    elif saldo_final == 0:
        estado = "se encuentra al día con sus pagos."
    else:
        estado = "presenta saldo a favor."

    informe_ia = [
        f"Cliente: {cliente_nombre}",
        f"Ventas registradas: ${total_ventas}",
        f"Cobros registrados: ${total_cobros}",
        f"Saldo pendiente: ${saldo_final}",
        f"Analisis automatico: El cliente {estado}"
    ]

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="informe_cuenta_corriente.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    p.setFont("Helvetica-Bold", 18)
    p.drawString(170, height - 50, "INFORME CUENTA CORRIENTE")

    p.setFont("Helvetica", 10)
    texto = p.beginText(40, height - 90)

    for linea in informe_ia:
        texto.textLine(linea)

    p.drawText(texto)

    p.rect(40, height - 190, 160, 50)
    p.drawString(80, height - 165, "TOTAL VENTAS")
    p.drawString(95, height - 180, f"${total_ventas}")

    p.rect(220, height - 190, 160, 50)
    p.drawString(255, height - 165, "TOTAL COBROS")
    p.drawString(275, height - 180, f"${total_cobros}")

    p.rect(400, height - 190, 160, 50)
    p.drawString(430, height - 165, "SALDO FINAL")
    p.drawString(455, height - 180, f"${saldo_final}")

    y = height - 260

    columnas = [
        ("Fecha", 40, 70),
        ("Cliente", 110, 130),
        ("Descripción", 240, 140),
        ("Venta", 380, 60),
        ("Cobro", 440, 60),
        ("Saldo", 500, 60),
    ]

    p.setFillColor(colors.black)
    for titulo, x, ancho in columnas:
        p.rect(x, y, ancho, 25, fill=1)

    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 9)

    for titulo, x, ancho in columnas:
        p.drawString(x + 5, y + 8, titulo)

    y -= 25
    p.setFillColor(colors.black)
    p.setFont("Helvetica", 8)

    for mov in movimientos:
        if y < 50:
            p.showPage()
            y = height - 50

        datos = [
            (mov.fecha.strftime("%d/%m/%Y"), 40, 70),
            (mov.cliente.nombre[:20], 110, 130),
            (mov.descripcion[:25], 240, 140),
            (f"${mov.total}", 380, 60),
            (f"${mov.pago}", 440, 60),
            (f"${mov.saldo}", 500, 60),
        ]

        for texto, x, ancho in datos:
            p.rect(x, y, ancho, 25)
            p.drawString(x + 3, y + 8, str(texto))

        y -= 25

    p.save()
    return response

def informe_ventas(request):
    ventas = Venta.objects.select_related('cliente').prefetch_related(
        'detalleventa_set__producto'
    ).all().order_by('-fecha')

    cliente_id = request.GET.get('cliente')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')

    if cliente_id:
        ventas = ventas.filter(cliente_id=cliente_id)

    if fecha_desde:
        ventas = ventas.filter(fecha__gte=fecha_desde)

    if fecha_hasta:
        ventas = ventas.filter(fecha__lte=fecha_hasta)

    clientes = Cliente.objects.all()

    total_general = 0
    for venta in ventas:
        for detalle in venta.detalleventa_set.all():
            total_general += detalle.subtotal

    return render(request, 'ventas/informe_ventas.html', {
        'ventas': ventas,
        'clientes': clientes,
        'total_general': total_general,
        'cliente_id': cliente_id,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
    })