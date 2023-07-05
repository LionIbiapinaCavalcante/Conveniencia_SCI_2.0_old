from django.urls import path
from . import views

urlpatterns = [
    path('relatorios/', views.Relatorios, name='Relatorios'),
    path('relatorios/total_consumido', views.RelatorioTotalConsumido, name='RelatorioTotalConsumido'),
    path('relatorios/consumo_detalhado', views.RelatorioConsumoDetalhado, name='RelatorioConsumoDetalhado'),
]