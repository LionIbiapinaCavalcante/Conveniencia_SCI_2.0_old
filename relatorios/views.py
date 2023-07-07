from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime, date, timedelta
import calendar
from registro_de_compras.models import RegistroCompra
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from reportlab.pdfgen import canvas



def Relatorios(request):
    return render(request, 'relatorios/relatorios.html')


def VisualizarRelatorioTotal(request):
    show_relatorio_total = False

    if request.method == 'POST':
        show_relatorio_total = True

        data_atual = datetime.now().date()

        if data_atual.day >= 26:
            inicio_referencia_atual = data_atual.replace(day=26)
            ultimo_dia_mes = calendar.monthrange(data_atual.year, data_atual.month)[1]
            fim_referencia_atual = data_atual.replace(day=ultimo_dia_mes)
        else:
            mes_anterior_2 = data_atual.replace(day=1) - timedelta(days=1)
            inicio_referencia_atual = mes_anterior_2.replace(day=26)
            fim_referencia_atual = data_atual.replace(day=25)

        compras_referencia_atual = RegistroCompra.objects.filter(data_compra__range=(inicio_referencia_atual, fim_referencia_atual))

        total_consumido = 0
        table_data = []
        
        for compra in compras_referencia_atual:
            table_data.append([compra.colaborador.nome, compra.data_compra.strftime('%d/%m/%Y'), f'R${compra.total_compra:.2f}'.replace('.', ',')])
            total_consumido += compra.total_compra

        render_total_consumido = (f'Total Consumido: R${total_consumido:.2f}'.replace('.', ','))

        return render(request, 'relatorios/relatorios.html', {'table_data': table_data, 'render_total_consumido': render_total_consumido, 'show_relatorio_total': show_relatorio_total})

def RelatorioConsumoDetalhado(request):
    return HttpResponse('Consumo Detalhado')


def GerarRelatorioTotal(request):
    # Data atual
    data_atual = datetime.now().date()

    # Cálculo referência mês atual
    if data_atual.day >= 26:
        inicio_referencia_atual = data_atual.replace(day=26)
        ultimo_dia_mes = calendar.monthrange(data_atual.year, data_atual.month)[1]
        fim_referencia_atual = data_atual.replace(day=ultimo_dia_mes)
    
    else:
        mes_anterior_2 = data_atual.replace(day=1) - timedelta(days=1)
        inicio_referencia_atual = mes_anterior_2.replace(day=26)
        fim_referencia_atual = data_atual.replace(day=25)

    compras_referencia_atual = RegistroCompra.objects.filter(data_compra__range=(inicio_referencia_atual, fim_referencia_atual))

    # Criação do documento PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_total_consumido.pdf"'
    buffer = BytesIO()

    # Criação do documento PDF usando o ReportLab
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Título do relatório
    title = Paragraph("Relatório Total Consumido", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 20))

    # Cabeçalho da tabela
    table_data = [['Colaborador', 'Data Compra', 'Valor']]
    for compra in compras_referencia_atual:
        table_data.append([compra.colaborador.nome, compra.data_compra.strftime('%d/%m/%Y'), f'R${compra.total_compra:.2f}'.replace('.', ',')])

    # Criação da tabela
    table = Table(table_data, colWidths=[150, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2D3560')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F3F8FA')),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(table)

    # Gera o PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response