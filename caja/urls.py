from django.urls import path
from . import views

app_name = "caja"

urlpatterns = [
    path("", views.caja_home, name="home"),
    path("abrir/", views.abrir_caja, name="abrir_caja"),
    path("cerrar/<int:pk>/", views.cerrar_caja, name="cerrar_caja"),
    path("movimientos/", views.movimientos, name="movimientos"),
    path("nuevo/", views.nuevo_movimiento, name="nuevo_movimiento"),
    path('arqueo/', views.arqueo, name='arqueo'),
    path("recibo/<int:pk>/", views.recibo_movimiento, name="recibo_movimiento"),
    path("movimientos/fecha/", views.movimientos_por_fecha, name="movimientos_por_fecha"),
]
