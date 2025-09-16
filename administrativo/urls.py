from django.urls import path
from . import views


app_name = "administrativo"

urlpatterns = [
    path("", views.administrativo_home, name="home"),

    # DOCUMENTOS
    path("documentos/", views.documentos_admin, name="documentos"),
    path("documentos/nuevo/", views.nuevo_documento_admin, name="nuevo_documento"),
    path("documentos/eliminar/<int:id>/", views.eliminar_documento_admin, name="eliminar_documento"),

    # HONORARIOS
    path("honorarios/", views.carga_honorarios, name="carga_honorarios"),
    path('cliente/<int:cliente_id>/honorarios/', views.lista_honorarios_cliente, name='lista_honorarios_cliente'),
    path('cliente/<int:cliente_id>/honorarios/nuevo/', views.nuevo_honorario_cliente, name='nuevo_honorario_cliente'),
    path('honorarios/nuevo/', views.nuevo_honorario, name='nuevo_honorario'),
    path('honorarios/registrar-pago/', views.registrar_pago_honorario, name='registrar_pago_honorario'),
    path("honorarios/eliminar/<int:id>/", views.eliminar_honorario, name="eliminar_honorario"),

    # GESTIONES
    path("gestiones/", views.gestiones_admin, name="gestiones"),
    path("gestiones/nueva/", views.nueva_gestion_admin, name="nueva_gestion"),
    path("gestiones/eliminar/<int:id>/", views.eliminar_gestion_admin, name="eliminar_gestion"),
    path("gestiones/editar/<int:id>/", views.editar_gestion_admin, name="editar_gestion"),
    
]
