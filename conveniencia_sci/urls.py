from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('usuarios.urls')),
    path('', include('dashboard.urls')),
    path('', include('colaboradores.urls')),
    path('', include('produtos.urls')),
    path('', include('registro_de_compras.urls')),
    path('', include('relatorios.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
