from django.contrib import admin
from django.urls import path, include  # <- aquí agregamos include
from django.conf import settings
from django.contrib.auth import views as auth_views
from clientes import views
from django.conf.urls.static import static

urlpatterns = [
    #iniciar sesion
    path('', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    #página principal
    path('index/', views.index, name='index'),
    path('admin/', admin.site.urls),
    path('clientes/', include('clientes.urls', namespace='clientes')),
    path('contable/', include(('contable.urls', 'contable'), namespace='contable')),
    path('caja/', include(('caja.urls', 'caja'), namespace='caja')),
    path('reportes/', include(('reportes.urls', 'reportes'), namespace='reportes')),
    path('administrativo/', include(('administrativo.urls', 'administrativo'), namespace='administrativo')),
    path('juridico/', include(('juridico.urls', 'juridico'), namespace='juridico')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)