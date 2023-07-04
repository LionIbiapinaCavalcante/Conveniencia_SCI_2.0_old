from django.urls import path
from . import views
from .views import CarrinhoCompras, LimparCarrinho, ExcluirProdutoCarrinho, TotalCarrinho, FinalizarCompra, GastoAtual


urlpatterns = [
    path('registro_de_compras/carrinho_de_compras', CarrinhoCompras.as_view(), name='CarrinhoCompras'),
    path('registro_de_compras/total_carrinho/', TotalCarrinho.as_view(), name='TotalCarrinho'),
    path('registro_de_compras/<int:produto_id>/excluir_produto_carrinho', ExcluirProdutoCarrinho.as_view(), name='ExcluirProdutoCarrinho'),
    path('registro_de_compras/limpar_carrinho/', LimparCarrinho.as_view(), name='LimparCarrinho'),
    path('registro_de_compras/finalizar_compra/', FinalizarCompra.as_view(), name='FinalizarCompra'),
    path('registro_de_compras/gasto_atual/', GastoAtual.as_view(), name='GastoAtual'),
]