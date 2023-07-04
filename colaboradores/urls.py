from django.urls import path
from . import views

urlpatterns = [
    path('colaboradores/', views.Colaboradores, name='Colaboradores'),
    path('colaboradores/cadastro/', views.CadastroColaborador, name='CadastroColaborador'),
    path('colaboradores/<int:colaborador_id>/editar/', views.EditarColaborador, name='EditarColaborador'),
]