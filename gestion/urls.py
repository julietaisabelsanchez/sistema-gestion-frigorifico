from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [

    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Login
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.register_view, name='registro'),

    # Password reset (Django built-in)
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),

    # Clientes
    path('clientes/', views.clientes, name='clientes'),
    path('agregar_cliente/', views.agregar_cliente, name='agregar_cliente'),
    path('editar_cliente/<int:id>/', views.editar_cliente, name='editar_cliente'),
    path('eliminar_cliente/<int:id>/', views.eliminar_cliente, name='eliminar_cliente'),

    # Productos
    path('productos/', views.productos, name='productos'),
    path('agregar_producto/', views.agregar_producto, name='agregar_producto'),
    path('agregar_produccion/', views.agregar_produccion, name='agregar_produccion'),
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

    # Envíos
    path('envios/', views.envios, name='envios'),
    path('envio/estado/<int:id>/', views.cambiar_estado_envio, name='cambiar_estado_envio'),

    # Dashboard Data
    path('dashboard/datos/', views.datos_dashboard, name='datos_dashboard'),

    # Deudas
    path('deudas/', views.deudas, name='deudas'),
    path('registrar-pago/<int:cliente_id>/', views.registrar_pago, name='registrar_pago'),
    path('eliminar_pago_cliente/<int:cliente_id>/', views.eliminar_pago_cliente, name='eliminar_pago_cliente'),
    path('recibo_pago_pdf/<int:cliente_id>/', views.recibo_pago_pdf, name='recibo_pago_pdf'),

    # Informes
    path('ventas/informe/', views.informe_ventas, name='informe_ventas'),
]