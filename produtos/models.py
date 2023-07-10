from django.db import models

class Produto(models.Model):
    CATEGORIA_CHOICES = (
        ('alimento', 'Alimento'),
        ('ingresso', 'Ingresso'),
        ('vestuario', 'Vestuário'),
    )

    nome = models.CharField(max_length=100)
    codigo_barras = models.CharField(max_length=5, unique=True)
    preco = models.DecimalField(max_digits=5, decimal_places=2)
    situacao = models.BooleanField(default=True)
    categoria = models.CharField(max_length=10, choices=CATEGORIA_CHOICES, default='alimento')
    
    def __str__(self) -> str:
        return self.nome
