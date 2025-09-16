from django.urls import path
from . import views

app_name = "juridico"

urlpatterns = [
    path("", views.juridico_home, name="home"),
    # Documentos
    path("documentos/", views.documentos_juridico, name="carga_documentos"),
    path("documentos/nuevo/", views.nuevo_documento_juridico, name="nuevo_documento"),
    path("documentos/eliminar/<int:id>/", views.eliminar_documento_juridico, name="eliminar_documento"),
    path('cliente/<int:cliente_id>/documentos/', views.lista_documentos_cliente, name='lista_documentos_cliente'),

    # Honorarios
    path("honorarios/", views.carga_honorarios, name="carga_honorarios"),
    path("honorarios/nuevo/", views.nuevo_honorario, name="nuevo_honorario"),
    path("honorarios/registrar-pago/", views.registrar_pago_honorario, name="registrar_pago_honorario"),
    path("honorarios/eliminar/<int:id>/", views.eliminar_honorario, name="eliminar_honorario"), 
    path('cliente/<int:cliente_id>/honorarios/', views.lista_honorarios_cliente, name='lista_honorarios_cliente'),

    # Gestiones
    path("gestiones/", views.carga_gestiones, name="carga_gestiones"),
    path("gestiones/nueva/", views.nueva_gestion, name="nueva_gestion"),
    path("gestiones/eliminar/<int:id>/", views.eliminar_gestion, name="eliminar_gestion"),
    path('cliente/<int:cliente_id>/gestiones/', views.lista_gestiones_cliente, name='lista_gestiones_cliente'),

]
