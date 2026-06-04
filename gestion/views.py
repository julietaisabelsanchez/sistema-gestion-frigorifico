import csv
import io
import json
import os
from decimal import Decimal
from datetime import date, datetime
from pathlib import Path

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

from .models import (
    Cliente,
    Producto,
    Produccion,
    Venta,
    DetalleVenta,
    Pago,
    Caja,
    MovimientoCaja,
    Empleado,
    Envio
)

from .forms import (
    EmpleadoForm,
    VentaForm
)


# =========================
# 🔐 LOGIN
# =========================
def login_view(request):
    if request.user.is_authenticated:
        return redirect('/')

    context = {}
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email or not password:
            context['error'] = 'El usuario y la contraseña son obligatorios.'
            context['email'] = email
            return render(request, "login.html", context)

        # Intenta autenticar usando el valor como username (por compatibilidad)
        user = authenticate(request, username=email, password=password)

        # Si no se autenticó, intenta buscar un usuario por email y usar su username
        if not user:
            try:
                user_obj = User.objects.get(email__iexact=email)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                # Si no existe un usuario Django para ese email, crearlo automáticamente
                # Esto ayuda a migrar usuarios que antes usaban Firebase o un sistema externo
                username_base = (email.split('@')[0]) if email else 'user'
                username_candidate = username_base
                suffix = 1
                while User.objects.filter(username=username_candidate).exists():
                    username_candidate = f"{username_base}{suffix}"
                    suffix += 1

                user = User.objects.create_user(username=username_candidate, email=email, password=password)
                user.save()
                # autenticar el usuario nuevo
                user = authenticate(request, username=username_candidate, password=password)
                if user:
                    messages.info(request, 'Cuenta creada automáticamente. Si no pediste esto, cambia tu contraseña.')

        if user is not None:
            login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next') or '/'
            return redirect(next_url)

        context['error'] = 'Usuario o contraseña incorrectos.'
        context['email'] = email

    return render(request, "login.html", context)


def logout_view(request):
    logout(request)
    return redirect('/login/')
    

def register_view(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        username = request.POST.get('username') or request.POST.get('email')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            messages.error(request, 'Email y contraseña son requeridos')
            return render(request, 'registro.html', {'email': email})

        # Evitar duplicados
        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'Ya existe un usuario con ese correo')
            return render(request, 'registro.html', {'email': email})

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, 'Cuenta creada correctamente. Inicia sesión.')
        return redirect('login')

    return render(request, 'registro.html')
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
            tipo='Producto',
            precio=request.POST.get('precio') or 0,
            stock=0
        )
        return redirect('productos')

    return render(request, 'agregar_producto.html')


def agregar_produccion(request):
    productos = Producto.objects.filter(nombre__icontains="grasa") | Producto.objects.filter(nombre__icontains="caja")
    context = {
        'productos': productos,
        'errors': [],
        'data': {}
    }

    if request.method == 'POST':
        producto_id = request.POST.get('producto')
        fecha = request.POST.get('fecha')
        cantidad = request.POST.get('cantidad')

        context['data'] = {
            'producto': producto_id,
            'fecha': fecha,
            'cantidad': cantidad
        }

        if not producto_id or not fecha or not cantidad:
            context['errors'].append('Todos los campos son obligatorios.')
        else:
            try:
                cantidad_int = int(cantidad)
                if cantidad_int <= 0:
                    raise ValueError

                producto = Producto.objects.get(id=int(producto_id))
                Produccion.objects.create(
                    producto=producto,
                    fecha=fecha,
                    cantidad=cantidad_int
                )

                producto.stock += cantidad_int
                producto.save()

                messages.success(request, 'Producción registrada y stock actualizado correctamente.')
                return redirect('stock_grasas_cajas')
            except (ValueError, Producto.DoesNotExist):
                context['errors'].append('Seleccione un producto válido y una cantidad mayor a 0.')

    return render(request, 'agregar_produccion.html', context)


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
        fecha_str = request.POST.get('fecha')
        numero_comprobante = request.POST.get('numero_comprobante')

        if cliente_id and producto_id and cantidad > 0:
            cliente = Cliente.objects.get(pk=cliente_id)
            producto = Producto.objects.get(pk=producto_id)

            if producto.stock >= cantidad:
                producto.stock -= cantidad
                producto.save()

                venta_fecha = date.today()
                if fecha_str:
                    try:
                        venta_fecha = date.fromisoformat(fecha_str)
                    except ValueError:
                        venta_fecha = date.today()

                if not numero_comprobante:
                    numero_comprobante = f"F-{Venta.objects.count() + 1:05d}"

                venta = Venta.objects.create(
                    cliente=cliente,
                    fecha=venta_fecha,
                    numero_comprobante=numero_comprobante
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
        total_venta = venta.detalleventa_set.aggregate(
            total=Sum('subtotal')
        ).get('total') or 0

    # 💰 TOTAL VENTAS
    total_ventas = Venta.objects.aggregate(
        total=Sum('detalleventa__subtotal')
    ).get('total') or 0

    # 💳 TOTAL PAGADO
    total_pagado_ventas = Venta.objects.aggregate(
        total=Sum('monto_pagado')
    ).get('total') or 0

    pagos_extra = Pago.objects.aggregate(
        total=Sum('monto')
    ).get('total') or 0

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

    export = request.GET.get('export')
    if export == 'excel':
        return export_deudas_csv(datos)

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


def export_ventas_csv(rows):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(['Fecha', 'Cliente', 'Ventas', 'Cobros', 'Deuda'])

    for row in rows:
        writer.writerow([
            row['fecha'].strftime('%d/%m/%Y'),
            row['cliente'],
            f"{row['ventas']:.2f}",
            f"{row['cobros']:.2f}",
            f"{row['deuda']:.2f}"
        ])

    response = HttpResponse(buffer.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="informe_ventas.csv"'
    return response


def export_ventas_pdf(rows, total_ventas, total_cobros, total_deuda):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="informe_ventas.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - 80

    p.setFont('Helvetica-Bold', 16)
    p.drawString(40, y, 'Informe de Ventas con Cobros y Deuda')
    y -= 30

    p.setFont('Helvetica', 11)
    p.drawString(40, y, f'Total ventas: ${total_ventas:,.2f}')
    p.drawString(260, y, f'Total cobros: ${total_cobros:,.2f}')
    p.drawString(460, y, f'Total deuda: ${total_deuda:,.2f}')
    y -= 40

    p.setFont('Helvetica-Bold', 10)
    p.drawString(40, y, 'Fecha')
    p.drawString(130, y, 'Cliente')
    p.drawString(300, y, 'Ventas')
    p.drawString(380, y, 'Cobros')
    p.drawString(450, y, 'Deuda')
    y -= 20

    p.setFont('Helvetica', 10)
    for row in rows:
        if y < 70:
            p.showPage()
            y = height - 50
            p.setFont('Helvetica-Bold', 10)
            p.drawString(40, y, 'Fecha')
            p.drawString(130, y, 'Cliente')
            p.drawString(300, y, 'Ventas')
            p.drawString(380, y, 'Cobros')
            p.drawString(450, y, 'Deuda')
            y -= 20
            p.setFont('Helvetica', 10)

        p.drawString(40, y, row['fecha'].strftime('%d/%m/%Y'))
        p.drawString(130, y, row['cliente'][:24])
        p.drawString(300, y, f"${row['ventas']:,.2f}")
        p.drawString(380, y, f"${row['cobros']:,.2f}")
        p.drawString(450, y, f"${row['deuda']:,.2f}")
        y -= 18

    p.showPage()
    p.save()
    return response


def export_deudas_csv(rows):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(['Cliente', 'Total Comprado', 'Total Pagado', 'Deuda'])

    for row in rows:
        writer.writerow([
            row['cliente'],
            f"{row['ventas']:.2f}",
            f"{row['pagos']:.2f}",
            f"{row['deuda']:.2f}"
        ])

    response = HttpResponse(buffer.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="deudas.csv"'
    return response


def informe_ventas(request):
    cliente_id = request.GET.get('cliente')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')

    ventas = Venta.objects.select_related('cliente').prefetch_related(
        'detalleventa_set__producto'
    ).all().order_by('-fecha')
    pagos = Pago.objects.select_related('cliente').all().order_by('-fecha')

    if cliente_id:
        ventas = ventas.filter(cliente_id=cliente_id)
        pagos = pagos.filter(cliente_id=cliente_id)

    if fecha_desde:
        ventas = ventas.filter(fecha__gte=fecha_desde)
        pagos = pagos.filter(fecha__date__gte=fecha_desde)

    if fecha_hasta:
        ventas = ventas.filter(fecha__lte=fecha_hasta)
        pagos = pagos.filter(fecha__date__lte=fecha_hasta)

    clientes = Cliente.objects.all()

    rows = {}
    for venta in ventas:
        total_venta = sum([detalle.subtotal for detalle in venta.detalleventa_set.all()])
        key = (venta.cliente_id, venta.fecha)
        if key not in rows:
            rows[key] = {
                'fecha': venta.fecha,
                'cliente': venta.cliente.nombre,
                'ventas': 0,
                'cobros': 0,
                'deuda': 0
            }
        rows[key]['ventas'] += total_venta

    for pago in pagos:
        pago_fecha = pago.fecha.date() if isinstance(pago.fecha, datetime) else pago.fecha
        key = (pago.cliente_id, pago_fecha)
        if key not in rows:
            rows[key] = {
                'fecha': pago_fecha,
                'cliente': pago.cliente.nombre,
                'ventas': 0,
                'cobros': 0,
                'deuda': 0
            }
        rows[key]['cobros'] += pago.monto

    report_rows = []
    for row in rows.values():
        row['deuda'] = row['ventas'] - row['cobros']
        report_rows.append(row)

    report_rows.sort(key=lambda item: (item['fecha'], item['cliente']))

    total_ventas = sum([row['ventas'] for row in report_rows])
    total_cobros = sum([row['cobros'] for row in report_rows])
    total_deuda = sum([row['deuda'] for row in report_rows])

    export = request.GET.get('export')
    if export == 'excel':
        return export_ventas_csv(report_rows)
    if export == 'pdf':
        return export_ventas_pdf(report_rows, total_ventas, total_cobros, total_deuda)

    return render(request, 'ventas/informe_ventas.html', {
        'ventas': report_rows,
        'clientes': clientes,
        'cliente_id': cliente_id,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'total_ventas': total_ventas,
        'total_cobros': total_cobros,
        'total_deuda': total_deuda,
    })


def eliminar_pago_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    Pago.objects.filter(cliente=cliente).delete()
    return redirect('deudas')




