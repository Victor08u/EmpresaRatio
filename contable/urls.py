from django.urls import path
from . import views

app_name = "contable"

urlpatterns = [
    path("", views.contable_home, name="home"),

    # DOCUMENTOS
    path("documentos/", views.carga_documentos, name="carga_documentos"),
    path("documentos/nuevo/", views.nuevo_documento, name="nuevo_documento"),
    path("documentos/eliminar/<int:id>/", views.eliminar_documento, name="eliminar_documento"),
    path('cliente/<int:cliente_id>/documentos/', views.lista_documentos_cliente, name='lista_documentos_cliente'),

    # HONORARIOS
    path("honorarios/", views.carga_honorarios, name="carga_honorarios"),
    path("honorarios/nuevo/", views.nuevo_honorario, name="nuevo_honorario"),
    path('cliente/<int:cliente_id>/honorarios/', views.lista_honorarios_cliente, name='lista_honorarios_cliente'),
    path('cliente/<int:cliente_id>/honorarios/nuevo/', views.nuevo_honorario_cliente, name='nuevo_honorario_cliente'),
    path('honorarios/registrar-pago/', views.registrar_pago_honorario, name='registrar_pago_honorario'),
    path("honorarios/eliminar/<int:id>/", views.eliminar_honorario, name="eliminar_honorario"),


    # GESTIONES
    path("gestiones/", views.carga_gestiones, name="carga_gestiones"),
    path("gestiones/nueva/", views.nueva_gestion, name="nueva_gestion"),
    path("gestiones/eliminar/<int:id>/", views.eliminar_gestion, name="eliminar_gestion"),
    path('cliente/<int:cliente_id>/gestiones/', views.lista_gestiones_cliente, name='lista_gestiones_cliente'),

    # VENCIMIENTOS
    path("vencimientos/", views.lista_vencimientos, name="lista_vencimientos"),
    path("vencimientos/nuevo/", views.nuevo_vencimiento, name="nuevo_vencimiento"),
    path("vencimientos/mover/<int:pk>/", views.marcar_recibido, name="marcar_recibido"),

]
