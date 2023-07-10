from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Produto
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages



@login_required(login_url='Login')
def Produtos(request):
    try:
        produtos = Produto.objects.all()
        return render(request, 'produtos/produtos.html', {'produtos': produtos})
    
    except Exception as e:
        print(str(e))
        error_message = ('Ocorreu um erro ao listar os produtos.')
        return render(request, 'produtos/produtos.html', {'error_message': error_message})
    

@csrf_protect
@login_required(login_url='Login')
def CadastroProduto(request):

    if request.method == 'POST':
        nome = request.POST.get('nome')
        codigo_barras = request.POST.get('codigo_barras')
        preco = request.POST.get('preco')
        categoria = request.POST.get('categoria')
        situacao = True if request.POST.get('situacao') == 'on' else False

        if not nome.strip():
            request.session['form_data'] = {'nome': nome, 'codigo_barras': codigo_barras, 'preco': preco}
            error_message = ('O campo nome não pode ser vazio.')
            messages.error(request, error_message)
            return redirect('CadastroProduto')

        if Produto.objects.filter(nome=nome).exists():
            request.session['form_data'] = {'nome': nome, 'codigo_barras': codigo_barras, 'preco': preco}
            error_message = ('Nome já cadastrado.')
            messages.error(request, error_message)
            return redirect('CadastroProduto')
        
        if not codigo_barras.strip():
            request.session['form_data'] = {'nome': nome, 'codigo_barras': codigo_barras, 'preco': preco}
            error_message = ('O campo código de barras não pode ser vazio.')
            messages.error(request, error_message)
            return redirect('CadastroProduto')
        
        if Produto.objects.filter(codigo_barras=codigo_barras).exists():
            request.session['form_data'] = {'nome': nome, 'codigo_barras': codigo_barras, 'preco': preco}
            error_message = ('Este código de barras já está cadastrado.')
            messages.error(request, error_message)
            return redirect('CadastroProduto')
            
        try:
            produto = Produto.objects.create(
                nome = nome,
                codigo_barras = codigo_barras,
                preco = preco,
                categoria = categoria,
                situacao = situacao
            )

            produto.save()
            request.session['form_data'] = {'nome': nome, 'codigo_barras': codigo_barras, 'preco': preco}
            success_message = ('Produto cadastrado com sucesso!')
            messages.success(request, success_message)
            return redirect('CadastroProduto')
        
        except Exception as e:
            print(e)
            error_message = 'Ocorreu um erro ao cadastrar o produto.'
            messages.error(request, error_message)
            return redirect('CadastroProduto')

    form_data = request.session.get('form_data', {})
    request.session['form_data'] = {}  
    return render(request, 'produtos/cadastro_produto.html', {'form_data': form_data})
    

@csrf_protect
@login_required(login_url='Login')
def EditarProduto(request, produto_id):
    if request.method == 'POST':
        produto = Produto.objects.get(pk=produto_id)
        
        nome = request.POST.get('nome')
        codigo_barras = request.POST.get('codigo_barras')
        preco = request.POST.get('preco')
        categoria = request.POST.get('categoria')
        situacao = True if request.POST.get('situacao') == 'on' else False

        if not nome.strip():
            error_message = ('O campo nome não pode ser vazio.')
            messages.error(request, error_message)
            redirect_url = reverse('EditarProduto', args=[produto_id])
            return redirect(redirect_url)

        if Produto.objects.exclude(pk=produto_id).filter(nome=nome).exists():
            error_message = ('Nome já cadastrado.')
            messages.error(request, error_message)
            redirect_url = reverse('EditarProduto', args=[produto_id])
            return redirect(redirect_url)
        
        if not codigo_barras.strip():
            error_message = ('O campo código de barras não pode ser vazio.')
            messages.error(request, error_message)
            redirect_url = reverse('EditarProduto', args=[produto_id])
            return redirect(redirect_url)
        
        if Produto.objects.exclude(pk=produto_id).filter(codigo_barras=codigo_barras).exists():
            error_message = ('Este código de barras já está cadastrado.')
            messages.error(request, error_message)
            redirect_url = reverse('EditarProduto', args=[produto_id])
            return redirect(redirect_url)
            
        try:
            produto.nome = nome
            produto.codigo_barras = codigo_barras
            produto.preco = preco
            produto.categoria = categoria
            produto.situacao = situacao
           
            print(categoria)
            produto.save()
            success_message = ('Dados do produto atualizados com sucesso!')
            messages.success(request, success_message)
            redirect_url = reverse('EditarProduto', args=[produto_id])
            return redirect(redirect_url)
        
        except Exception as e:
            print(str(e))
            error_message = ('Ocorreu um erro durante o processo de atualização dos dados do produto.')
            messages.error(request, error_message)
            redirect_url = reverse('EditarProduto', args=[produto_id])
            return redirect(redirect_url)
    
    try:
        produto = Produto.objects.get(pk=produto_id)
        return render(request, 'produtos/editar_produto.html', {'produto': produto, 'form_data': {'categoria': produto.categoria,}})
    
    except Exception as e:
        print(str(e))
        error_message = ('Ocorreu um erro ao tentar editar os dados do produto.')
        return render (request, 'produtos/editar_produto.html', {'error_mssage': error_message})
    