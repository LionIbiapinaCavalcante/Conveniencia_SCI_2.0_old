from django.urls import path
from . import views

urlpatterns = [
    path('relatorios/', views.Relatorios, name='Relatorios'),
]