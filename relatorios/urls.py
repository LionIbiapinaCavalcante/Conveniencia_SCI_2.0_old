from django.urls import path
from . import views

urlpatterns = [
    path('relatorios/', views.Relatorios, name='Relatorios'),
    path('relatorios/total_consumido', views.VisualizarRelatorioTotal, name='VisualizarRelatorioTotal'),
    path('relatorios/total_consumido/gerar_pdf', views.GerarRelatorioTotal, name='GerarRelatorioTotal'),
    path('relatorios/consumo_detalhado', views.RelatorioConsumoDetalhado, name='RelatorioConsumoDetalhado'),
]