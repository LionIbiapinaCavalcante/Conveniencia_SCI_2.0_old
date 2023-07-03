from django.db import models
from produtos.models import Produto
from colaboradores.models import Colaborador

class RegistroCompra(models.Model):
    produto = models.ManyToManyField(Produto, through='ItemCompra')
    colaborador = models.ForeignKey(Colaborador, on_delete=models.CASCADE)
    data_compra = models.DateField()

    def __str__(self) -> str:
        return f"Compra de {self.colaborador.nome} em {self.data_compra}"
    
class ItemCompra(models.Model):
    registro_compra = models.ForeignKey('RegistroCompra', on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.IntegerField(default=1)
    valor = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self) -> str:
        return f"Compra: {self.registro_compra}, Produto: {self.produto}"