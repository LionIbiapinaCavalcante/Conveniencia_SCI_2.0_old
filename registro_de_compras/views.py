from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from produtos.models import Produto
from colaboradores.models import Colaborador
from registro_de_compras.models import RegistroCompra
from registro_de_compras.models import ItemCompra
from django.views import View
from django.contrib.auth.hashers import check_password
from datetime import datetime, date, timedelta
import calendar
from django.contrib import messages


# def CarrinhoCompras(request):
#     compras = AddProdutoCarrinho.carrinho

#     return render(request,'registro_de_compras/carrinho_de_compras.html', {'compras': compras})



class CarrinhoCompras(View):
    carrinho = []

    def get(self, request):
        compras = self.carrinho
        return render(request, 'registro_de_compras/carrinho_de_compras.html', {'compras': compras})

    def post(self, request):
        codigo_barras = request.POST.get('produto')

        try:
            if Produto.objects.filter(codigo_barras=codigo_barras).exists():
                produto = Produto.objects.get(codigo_barras=codigo_barras)
                self.carrinho.append(produto)
                return redirect('CarrinhoCompras')
            
            else:
                error_message = 'Produto não encontrado'
                messages.error(request, error_message)
                return redirect('CarrinhoCompras')

        except Produto.DoesNotExist as e:
            print(str(e))
            error_message = ('Ocorreu um erro ao buscar o produto')
            messages.error(request, error_message)
            return redirect('CarrinhoCompras')


class TotalCarrinho(View):
    def get(self, request):
        carrinho = CarrinhoCompras.carrinho
        total = sum(produto.preco for produto in carrinho)

        return HttpResponse(total)


class ExcluirProdutoCarrinho(View):
    def get(self, request, produto_id):
        produto = Produto.objects.get(id=produto_id)
        CarrinhoCompras.carrinho.remove(produto)
     
        return redirect('CarrinhoCompras')



class LimparCarrinho(View):
    def get(self, request):
        CarrinhoCompras.carrinho = []
        return redirect('CarrinhoCompras')
    
    def post(self, request):
        CarrinhoCompras.carrinho = []
        return redirect('CarrinhoCompras')
    


class FinalizarCompra(View):
    def post(self, request):
        login_colaborador = request.POST.get('login_colaborador')
        senha = request.POST.get('senha')

        compras = CarrinhoCompras.carrinho

        try:
            colaborador = Colaborador.objects.get(login=login_colaborador)

            if check_password(senha, colaborador.senha):

                if colaborador.situacao:
                    carrinho = CarrinhoCompras.carrinho

                    compra = RegistroCompra.objects.create(colaborador=colaborador, data_compra=date.today())

                    total_compra = sum(item.preco for item in carrinho)
                    compra.total_compra = total_compra
                    compra.save()

                    for item in carrinho:
                        ItemCompra.objects.create(registro_compra=compra, produto=item, valor=item.preco)

                    CarrinhoCompras.carrinho = []


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

                    # Filtrar as compras das refrências
                    compras_referencia_anterior = RegistroCompra.objects.filter(data_compra__range=(inicio_referencia_anterior, fim_referencia_anterior), colaborador=colaborador)
                    compras_referencia_atual = RegistroCompra.objects.filter(data_compra__range=(inicio_referencia_atual, fim_referencia_atual), colaborador=colaborador)

                    # Calcule o gasto do período
                    gasto_referencia_anterior = round(sum(item.valor for compra in compras_referencia_anterior for item in compra.itemcompra_set.all()), 2)
                    gasto_referencia_atual = round(sum(item.valor for compra in compras_referencia_atual for item in compra.itemcompra_set.all()), 2)

                    return render(request, 'registro_de_compras/carrinho_de_compras.html', {'show_modal': True, 'colaborador': colaborador, 'gasto_referencia_anterior': gasto_referencia_anterior, 'gasto_referencia_atual': gasto_referencia_atual})

                else:
                    error_message = ('Colaborador inativo.')
                    messages.error(request, error_message)
                    return redirect('CarrinhoCompras')
            
            else:
                error_message = ('Login ou senha incorretos.')
                messages.error(request, error_message)
                return redirect('CarrinhoCompras')
                
        except Exception as e:
            print(str(e))
            error_message = ('Ocorreu um erro ao tentar realizar o login.')
            messages.error(request, error_message)
            return redirect('CarrinhoCompras')
    

class GastoAtual(View):
    def post(self, request):
        login_colaborador = request.POST.get('login_colaborador')
        senha = request.POST.get('senha')

        compras = CarrinhoCompras.carrinho

        try:
            colaborador = Colaborador.objects.get(login=login_colaborador)

            if check_password(senha, colaborador.senha):

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

                # Filtrar as compras das refrências
                compras_referencia_anterior = RegistroCompra.objects.filter(data_compra__range=(inicio_referencia_anterior, fim_referencia_anterior), colaborador=colaborador)
                compras_referencia_atual = RegistroCompra.objects.filter(data_compra__range=(inicio_referencia_atual, fim_referencia_atual), colaborador=colaborador)

                # Calcule o gasto do período
                gasto_referencia_anterior = round(sum(item.valor for compra in compras_referencia_anterior for item in compra.itemcompra_set.all()), 2)
                gasto_referencia_atual = round(sum(item.valor for compra in compras_referencia_atual for item in compra.itemcompra_set.all()), 2)

                return render(request, 'registro_de_compras/carrinho_de_compras.html', {'show_modal': True, 'compras': compras, 'colaborador': colaborador, 'gasto_referencia_anterior': gasto_referencia_anterior, 'gasto_referencia_atual': gasto_referencia_atual})
                
            else:
                print('Login inválido')
                error_message = ('Login ou senha incorretos.')
                messages.error(request, error_message)
                return redirect('CarrinhoCompras')
                
        except Exception as e:
            print(str(e))
            error_message = ('Ocorreu um erro ao tentar realizar o login.')
            messages.error(request, error_message)
            return redirect('CarrinhoCompras')
        