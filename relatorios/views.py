from django.shortcuts import render
from django.http import HttpResponse

def Relatorios(request):
    return render(request, 'relatorios/relatorios.html')
