from django.urls import path
from . import views

app_name = "reportes"

urlpatterns = [
    path("", views.reportes_home, name="home"),
    path("index/", views.reporte_index, name="reporte_index"),
    path('auditoria/', views.reporte_auditoria, name='auditoria'),


]
