from django.urls import path
from . import views

urlpatterns = [
    path('', views.Login, name='Login'),
    path('usuarios/', views.Usuarios, name='Usuarios'),
    path('fomulario/', views.FormularioView.as_view(), name='FormularioView'),
    path('usuarios/cadastro/', views.CadastroUsuario, name='CadastroUsuario'),
    # path('usuarios/<int:usuario_id>/editar/', views.EditarUsuario, name='EditarUsuario'),
    path('usuarios/<int:usuario_id>/editar/', views.EditarUsuario, name='EditarUsuario'),
    path('usuarios/<int:usuario_id>/excluir/', views.ExcluirUsuario, name='ExcluirUsuario'),
    path('logout/', views.Logout, name='Logout'),
]