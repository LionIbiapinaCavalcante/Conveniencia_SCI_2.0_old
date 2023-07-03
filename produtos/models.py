from django.db import models

class Produto(models.Model):
    nome = models.CharField(max_length=100)
    codigo_barras = models.CharField(max_length=5, unique=True)
    preco = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self) -> str:
        return self.nome
