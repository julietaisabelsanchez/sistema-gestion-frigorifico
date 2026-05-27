from django.urls import path
from . import views

urlpatterns = [

    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Login
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),
    path('verificar_token/', views.verificar_token),

    # Clientes
    path('clientes/', views.clientes, name='clientes'),
    path('agregar_cliente/', views.agregar_cliente, name='agregar_cliente'),
    path('editar_cliente/<int:id>/', views.editar_cliente, name='editar_cliente'),
    path('eliminar_cliente/<int:id>/', views.eliminar_cliente, name='eliminar_cliente'),

    # Productos
    path('productos/', views.productos, name='productos'),
    path('agregar_producto/', views.agregar_producto, name='agregar_producto'),
    path('editar_producto/<int:id>/', views.editar_producto, name='editar_producto'),
    path('producto/eliminar/<int:id>/', views.eliminar_producto, name='eliminar_producto'),
    path('producto/stock/<int:id>/', views.cambiar_stock, name='cambiar_stock'),

    # Stock
    path('stock/', views.stock_grasas_cajas, name='stock_grasas_cajas'),

    # Ventas
    path('ventas/', views.ventas, name='ventas'),
    path('factura/<int:venta_id>/', views.factura_pdf, name='factura_pdf'),
    path('editar-venta/<int:id>/', views.editar_venta, name='editar_venta'),
    

    # Empleados
    path('empleados/', views.empleados, name='empleados'),
    path('empleados/agregar/', views.agregar_empleado, name='agregar_empleado'),
    path('empleados/editar/<int:id>/', views.editar_empleado, name='editar_empleado'),
    path('empleados/eliminar/<int:id>/', views.eliminar_empleado, name='eliminar_empleado'),

    # Caja
    path('caja/', views.caja, name='caja'),
    path('caja/pdf/', views.caja_pdf, name='caja_pdf'),

    # Envios
    path('envios/', views.envios, name='envios'),
    path('envio/estado/<int:id>/', views.cambiar_estado_envio, name='cambiar_estado_envio'),

    # Dashboard data
    path('dashboard/datos/', views.datos_dashboard, name='datos_dashboard'),

    # Deudas
    path('deudas/', views.deudas, name='deudas'),
    path('registrar-pago/<int:cliente_id>/', views.registrar_pago, name='registrar_pago'),
    # Cuenta Corriente
    path('cuenta-corriente/', views.cuenta_corriente, name='cuenta_corriente'),
    path('cuenta-corriente/nuevo/', views.nueva_cuenta_corriente, name='nueva_cuenta_corriente'),
    path('cuenta-corriente/editar/<int:id>/', views.editar_cuenta_corriente, name='editar_cuenta_corriente'),
    path('editar_venta/<int:id>/', views.editar_venta, name='editar_venta'),
    path('eliminar_pago_cliente/<int:cliente_id>/', views.eliminar_pago_cliente, name='eliminar_pago_cliente'),
    path('recibo_pago_pdf/<int:cliente_id>/', views.recibo_pago_pdf, name='recibo_pago_pdf'),
    path('informe-cuenta-corriente/', views.informe_cuenta_corriente, name='informe_cuenta_corriente'),
    path('informe-cuenta-corriente/pdf/', views.informe_cuenta_corriente_pdf, name='informe_cuenta_corriente_pdf'),
    path('cuenta-corriente/editar/<int:id>/', views.editar_cuenta_corriente, name='editar_cuenta_corriente'),
    path('ventas/informe/', views.informe_ventas, name='informe_ventas'),   
    path('ventas/informe/', views.informe_ventas, name='informe_ventas'),
]