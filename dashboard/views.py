from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime, date, timedelta
from django.db.models import Sum
import calendar
from registro_de_compras.models import RegistroCompra



@login_required(login_url='Login')
def DashBoard(request):
   # Data atual
    data_atual = datetime.now().date()

    # Cálculo referência mês anterior
    if data_atual.day >= 26:
        mes_anterior = data_atual.replace(day=1) - timedelta(days=1)
        inicio_referencia_anterior = mes_anterior.replace(day=26)
        fim_referencia_anterior = data_atual.replace(day=25)
    
    else:    
        mes_anterior = data_atual.replace(day=1) - timedelta(days=1)
        dois_meses_atras = mes_anterior.replace(day=1) - timedelta(days=1)
        inicio_referencia_anterior = dois_meses_atras.replace(day=26)
        fim_referencia_anterior = mes_anterior.replace(day=25)
    
    # Cálculo referência mês atual
    if data_atual.day >= 26:
        inicio_referencia_atual = data_atual.replace(day=26)
        ultimo_dia_mes = calendar.monthrange(data_atual.year, data_atual.month)[1]
        fim_referencia_atual = data_atual.replace(day=ultimo_dia_mes)
    
    else:
        mes_anterior_2 = data_atual.replace(day=1) - timedelta(days=1)
        inicio_referencia_atual = mes_anterior_2.replace(day=26)
        fim_referencia_atual = data_atual.replace(day=25)

    # Filtrar as compras das referências
    compras_referencia_anterior = RegistroCompra.objects.filter(data_compra__range=(inicio_referencia_anterior, fim_referencia_anterior))    
    compras_referencia_atual = RegistroCompra.objects.filter(data_compra__range=(inicio_referencia_atual, fim_referencia_atual))

    valor_referencia_anterior = sum(item.valor for compra in compras_referencia_anterior for item in compra.itemcompra_set.all())
    valor_referencia_atual = sum(item.valor for compra in compras_referencia_atual for item in compra.itemcompra_set.all())


    contexto = {
        'valor_referencia_anterior': valor_referencia_anterior,
        'valor_referencia_atual': valor_referencia_atual,
    }

    return render(request, 'dashboard/dashboard.html', contexto)