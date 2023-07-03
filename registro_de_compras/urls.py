from django.urls import path
from . import views
from .views import AddProdutoCarrinho, LimparCarrinho, ExcluirProdutoCarrinho, TotalCarrinho, FinalizarCompra, GastoAtual


urlpatterns = [
    path('registro_de_compras/', views.CarrinhoCompras, name='CarrinhoCompras'),
    path('registro_de_compras/add_produto_carrinho/', AddProdutoCarrinho.as_view(), name='AddProdutoCarrinho'),
    path('registro_de_compras/total_carrinho/', TotalCarrinho.as_view(), name='TotalCarrinho'),
    path('registro_de_compras/<int:produto_id>/excluir_produto_carrinho', ExcluirProdutoCarrinho.as_view(), name='ExcluirProdutoCarrinho'),
    path('registro_de_compras/limpar_carrinho/', LimparCarrinho.as_view(), name='LimparCarrinho'),
    path('registro_de_compras/finalizar_compra/', FinalizarCompra.as_view(), name='FinalizarCompra'),
    path('registro_de_compras/gasto_atual/', GastoAtual.as_view(), name='GastoAtual'),
]