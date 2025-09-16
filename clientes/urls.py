from django.urls import path
from . import views
app_name = "clientes" 
urlpatterns = [
    path('', views.lista_clientes, name='listar'),  # <-- la principal
    path('nuevo/', views.nuevo_cliente, name='nuevo_cliente'),
    path('<int:pk>/editar/', views.editar_cliente, name='editar_cliente'),
    path('<int:pk>/eliminar/', views.eliminar_cliente, name='eliminar_cliente'),
    path('inactivar/<int:id>/', views.inactivar_cliente, name='inactivar_cliente'),
    path('activar/<int:id>/', views.activar_cliente, name='activar_cliente'),
]