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
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors


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

                if produto.situacao:
                    self.carrinho.append(produto)
                    return redirect('CarrinhoCompras')
                
                else:
                    error_message = 'Produto inativo'
                    messages.error(request, error_message)
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

                    # Envio de email após finalização da compra
                    data = timezone.localtime(timezone.now())
                    data_formatada = data.strftime('%d/%m/%Y')
                    hora_formatada = data.strftime('%H:%M:%S')

                  # Código para gerar o PDF
                    pdf_filename = 'compra_realizada.pdf'  # Nome do arquivo PDF gerado
                    GerarPdfCompra(colaborador.nome, data_formatada, hora_formatada, carrinho, total_compra)

                    # Construção do e-mail
                    email = EmailMultiAlternatives('Confirmação de Compra Conveniência SCI 2.0', '', settings.EMAIL_HOST_USER, ['lioncavalcantebnu@gmail.com'])
                    email.attach_file(pdf_filename)  # Anexa o arquivo PDF ao e-mail

                    # Construção do conteúdo do e-mail
                    html_content = render_to_string('email/compra_realizada.html', {'colaborador': colaborador, 'carrinho': carrinho, 'data_formatada': data_formatada, 'hora_formatada': hora_formatada, 'total_compra': total_compra})
                    text_content = strip_tags(html_content)
                    email.attach_alternative(html_content, 'text/html')
                    email.send()

                    # verificação da referência
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
        

def GerarPdfCompra(nome_colaborador, data_compra, hora_compra, carrinho, total_compra):
    pdf_filename = 'compra_realizada.pdf'

    # Crie um objeto SimpleDocTemplate com o nome do arquivo PDF e o tamanho da página
    doc = SimpleDocTemplate(pdf_filename, pagesize=A4)

    # Defina o estilo padrão do documento
    style_sheet = getSampleStyleSheet()
    title_style = style_sheet['Title']
    subtitle_style = style_sheet['Heading3']
    subtitle_style.spaceAfter = 0  # Remover o espaçamento após o subtítulo
    normal_style = style_sheet['Normal']
    bold_style = style_sheet['Heading1']

    # Crie uma lista para armazenar os elementos do PDF
    elements = []

    # Adicione o título do documento
    title = Paragraph("Conveniência SCI 2.0", title_style)
    elements.append(title)

    # Adicione o subtítulo "Compra realizada" sem itálico e sem espaçamento após
    subtitle = Paragraph("Compra realizada", subtitle_style)
    subtitle_style.fontName = 'Helvetica-Bold'  # Definir a fonte em negrito
    subtitle_style.spaceAfter = 0  # Remover o espaçamento após o subtítulo
    elements.append(subtitle)

    # Adicione o nome do colaborador
    nome_colab = Paragraph(f"Colaborador(a): {nome_colaborador}", normal_style)
    elements.append(nome_colab)

    # Adicione a data e hora da compra
    data_hora = Paragraph(f"Data da Compra: {data_compra}<br/>Hora da Compra: {hora_compra}", normal_style)
    elements.append(data_hora)

    # Adicione um espaço em branco maior
    elements.append(Spacer(1, 0.4 * inch))  # Ajuste o tamanho do espaçamento conforme necessário

    # Crie uma lista de dados da tabela
    data = [['Produto', 'Preço', 'Quantidade']]

    # Adicione os itens do carrinho na tabela
    for produto in carrinho:
        nome = produto.nome
        preco = produto.preco
        data.append([nome, preco, '1'])

    # Ajuste as margens da tabela
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2D3560")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#FFFFFF")),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#000000")),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ])

    # Crie uma tabela com os dados e aplique o estilo
    table = Table(data)
    table.setStyle(table_style)

    # Defina a largura desejada para cada coluna (em pontos)
    col_widths = [280, 80, 80]  # Larguras das colunas em pontos

    # Ajuste as larguras das colunas da tabela
    table._argW[0] = col_widths[0]
    table._argW[1] = col_widths[1]
    table._argW[2] = col_widths[2]

    # Adicione a tabela ao documento
    elements.append(table)

    # Adicione o valor total abaixo da tabela
    total_compra_text = "Total da Compra: " + str(total_compra)
    total_compra_paragraph = Paragraph(total_compra_text, subtitle_style)
    elements.append(total_compra_paragraph)

    # Construa o documento PDF com os elementos
    doc.build(elements)