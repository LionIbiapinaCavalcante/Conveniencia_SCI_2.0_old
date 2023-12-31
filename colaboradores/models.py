from django.db import models

class Colaborador (models.Model):
    nome = models.CharField(max_length=150)
    cpf = models.CharField(max_length=11, unique=True)
    login = models.CharField(max_length=50, unique=True)
    senha = models.CharField(max_length=100)
    situacao = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.nome