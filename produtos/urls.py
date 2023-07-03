from django.urls import path
from . import views

urlpatterns = [
    path('produtos/', views.Produtos, name='Produtos'),
    path('produtos/cadastro/', views.CadastroProduto, name='CadastroProduto'),
    path('produtos/<int:produto_id>/editar/', views.EditarProduto, name='EditarProduto'),
    # path('produtos/<int:produto_id>/update/', views.UpdateProduto, name='UpdateProduto'),
]