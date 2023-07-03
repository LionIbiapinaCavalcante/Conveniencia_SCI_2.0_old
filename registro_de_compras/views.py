from django.shortcuts import render, redirect
from django.http import HttpResponse
from produtos.models import Produto
from colaboradores.models import Colaborador
from registro_de_compras.models import RegistroCompra
from registro_de_compras.models import ItemCompra
from django.views import View
from django.contrib.auth.hashers import check_password
from datetime import datetime, date, timedelta
from django.db.models import Sum
import calendar


def CarrinhoCompras(request):
    compras = AddProdutoCarrinho.carrinho

    return render(request,'registro_de_compras/carrinho_de_compras.html', {'compras': compras})



class AddProdutoCarrinho(View):
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

                return redirect('AddProdutoCarrinho')

            else:
                compras = self.carrinho
                
                return render(request, 'registro_de_compras/carrinho_de_compras.html', {'compras': compras, 'error_message': 'Produto não encontrado'})


        except Produto.DoesNotExist as e:
            print(str(e))
            compras = self.carrinho

            return render(request, 'registro_de_compras/carrinho_de_compras.html', {'compras': compras, 'error_message': 'Produto não encontrado'})


class TotalCarrinho(View):
    def get(self, request):
        carrinho = AddProdutoCarrinho.carrinho
        total = sum(produto.preco for produto in carrinho)

        return HttpResponse(total)


class ExcluirProdutoCarrinho(View):
    def get(self, request, produto_id):
        produto = Produto.objects.get(id=produto_id)
        AddProdutoCarrinho.carrinho.remove(produto)
     
        return redirect('AddProdutoCarrinho')



class LimparCarrinho(View):
    def get(self, request):
        AddProdutoCarrinho.carrinho = []

        return redirect('CarrinhoCompras')
    
    def post(self, request):
        AddProdutoCarrinho.carrinho = []

        return redirect('CarrinhoCompras')
    


class FinalizarCompra(View):
    def post(self, request):
        login_colaborador = request.POST.get('login_colaborador')
        senha = request.POST.get('senha')

        compras = AddProdutoCarrinho.carrinho

        try:
            colaborador = Colaborador.objects.get(login=login_colaborador)

            if check_password(senha, colaborador.senha):

                if colaborador.situacao:
                    carrinho = AddProdutoCarrinho.carrinho

                    compra = RegistroCompra.objects.create(colaborador=colaborador, data_compra=date.today())

                    for item in carrinho:
                        ItemCompra.objects.create(registro_compra=compra, produto=item, valor=item.preco)

                    AddProdutoCarrinho.carrinho = []


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
                    return render(request, 'registro_de_compras/carrinho_de_compras.html', {'compras': compras, 'error_message': error_message})
            
            else:
                error_message = ('Login ou senha incorretos.')
                return render(request, 'registro_de_compras/carrinho_de_compras.html', {'compras': compras, 'error_message': error_message})
                
        except Exception as e:
            print(str(e))
            error_message = ('Ocorreu um erro ao tentar realizar o login.')

            return render(request, 'registro_de_compras/carrinho_de_compras.html', {'compras': compras, 'error_message': error_message})
    

class GastoAtual(View):
    def post(self, request):
        login_colaborador = request.POST.get('login_colaborador')
        senha = request.POST.get('senha')

        compras = AddProdutoCarrinho.carrinho

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

                return render(request, 'registro_de_compras/carrinho_de_compras.html', {'compras': compras, 'error_message': error_message})
                
        except Exception as e:
            print(str(e))
            error_message = ('Ocorreu um erro ao tentar realizar o login.')

            return render(request, 'registro_de_compras/carrinho_de_compras.html', {'compras': compras, 'error_message': error_message})
        