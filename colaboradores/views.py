from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Colaborador
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_protect



def validar_cpf(cpf):
    cpf = ''.join(filter(str.isdigit, cpf))

    if len(cpf) != 11:
        return False

    if cpf == cpf[0] * 11:
        return False

    return True


@login_required(login_url='Login')
def Colaboradores(request):
    try:
        colaboradores = Colaborador.objects.all()
        return render(request, 'colaboradores/colaboradores.html', {'colaboradores': colaboradores})
    
    except Exception as e:
        print(str(e))
        error_message = ('Ocorreu um erro ao listar os colaboradores.')
        return render(request, 'colaboradores/colaboradores.html', {'error_message': error_message})


@csrf_protect
@login_required(login_url='Login')
def CadastroColaborador(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        cpf = request.POST.get('cpf')
        login = request.POST.get('login')
        senha = request.POST.get('senha')
        confirma_senha = request.POST.get('confirma_senha')
        situacao = True if request.POST.get('situacao') == 'on' else False

        try:
            if not nome.strip():
                request.session['form_data'] = {'nome': nome, 'cpf': cpf, 'login': login}
                error_message = ('O campo nome não pode ser vazio.')
                messages.error(request, error_message)
                return redirect('CadastroColaborador')
            
            if Colaborador.objects.filter(nome=nome).exists():
                request.session['form_data'] = {'nome': nome, 'cpf': cpf, 'login': login}
                error_message = ('Nome já cadastrado.')
                messages.error(request, error_message)
                return redirect('CadastroColaborador')

            if not validar_cpf(cpf):
                request.session['form_data'] = {'nome': nome, 'cpf': cpf, 'login': login}
                error_message = 'CPF inválido.'
                messages.error(request, error_message)
                return redirect('CadastroColaborador')
                       
            if Colaborador.objects.filter(cpf=cpf).exists():
                request.session['form_data'] = {'nome': nome, 'cpf': cpf, 'login': login}
                error_message = ('Este CPF já está cadastrado.')
                messages.error(request, error_message)
                return redirect('CadastroColaborador')

            if not login.strip():
                request.session['form_data'] = {'nome': nome, 'cpf': cpf, 'login': login}
                error_message = ('O campo login não pode ser vazio.')
                messages.error(request, error_message)
                return redirect('CadastroColaborador')

            if Colaborador.objects.filter(login=login).exists():
                request.session['form_data'] = {'nome': nome, 'cpf': cpf, 'login': login}
                error_message = ('Login já cadastrado.')
                messages.error(request, error_message)
                return redirect('CadastroColaborador')

            if senha != confirma_senha:
                request.session['form_data'] = {'nome': nome, 'cpf': cpf, 'login': login}
                error_message = ('A confirmação da senha fornecida não corresponde com a senha informada.')
                messages.error(request, error_message)
                return redirect('CadastroColaborador')

            if len(senha) < 8:
                request.session['form_data'] = {'nome': nome, 'cpf': cpf, 'login': login}
                error_message = ('A senha precisa ter pelo menos 8 caracteres.')
                messages.error(request, error_message)
                return redirect('CadastroColaborador')

            hashed_password = make_password(senha)
            colaborador = Colaborador.objects.create(
                nome = nome,
                cpf = cpf,
                login = login,
                senha = hashed_password,
                situacao = situacao
            )

            colaborador.save()
            request.session['form_data'] = {'nome': nome, 'cpf': cpf, 'login': login}
            success_message = ('Colaborador cadastrado com sucesso!')
            messages.success(request, success_message)
            return redirect('CadastroColaborador')
        
        except Exception as e:
            print(e)
            request.session['form_data'] = {'nome': nome, 'cpf': cpf, 'login': login}
            error_message = 'Ocorreu um erro ao cadastrar o colaborador.'
            messages.error(request, error_message)
            return redirect('CadastroColaborador')
        
    form_data = request.session.get('form_data', {})
    request.session['form_data'] = {}    
    return render(request, 'colaboradores/cadastro_colaborador.html', {'form_data': form_data})


# @login_required(login_url='Login')
# def EditarColaborador(request, colaborador_id):
#     try:
#         colaborador = Colaborador.objects.get(pk=colaborador_id)
#         return render (request, 'colaboradores/editar_colaborador.html', {'colaborador': colaborador})
    
#     except Exception as e:
#         print(str(e))
#         error_message = ('Ocorreu um erro ao tentar editar os dados do colaborador.')
#         return render (request, 'colaboradores/editar_colaborador.html', {'error_mssage': error_message})


@csrf_protect
@login_required(login_url='Login')
def EditarColaborador(request, colaborador_id):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        cpf = request.POST.get('cpf')
        login = request.POST.get('login')
        colaborador.situacao = True if request.POST.get('situacao') == 'on' else False
        nova_senha = request.POST.get('nova_senha')
        confirma_nova_senha = request.POST.get('confirma_nova_senha')

        if not nome.strip():
            error_message = ('O campo nome não pode ser vazio.')
            messages.error(request, error_message)
            redirect_url = reverse('EditarColaborador', args=[colaborador_id])
            return redirect(redirect_url)


        if Colaborador.objects.exclude(pk=colaborador_id).filter(nome=nome).exists():
            error_message = ('Nome já cadastrado.')
            messages.error(request, error_message)
            redirect_url = reverse('EditarColaborador', args=[colaborador_id])
            return redirect(redirect_url)
                
        if not validar_cpf(cpf):
            error_message = 'CPF inválido.'
            messages.error(request, error_message)
            redirect_url = reverse('EditarColaborador', args=[colaborador_id])
            return redirect(redirect_url)

        if Colaborador.objects.exclude(pk=colaborador_id).filter(cpf=cpf).exists():
            error_message = ('CPF já cadastrado.')
            messages.error(request, error_message)
            redirect_url = reverse('EditarColaborador', args=[colaborador_id])
            return redirect(redirect_url)

        if not login.strip():
            error_message = ('O campo login não pode ser vazio.')
            messages.error(request, error_message)
            redirect_url = reverse('EditarColaborador', args=[colaborador_id])
            return redirect(redirect_url)

        if Colaborador.objects.exclude(pk=colaborador_id).filter(login=login).exists():
            error_message = ('Login já cadastrado.')
            messages.error(request, error_message)
            redirect_url = reverse('EditarColaborador', args=[colaborador_id])
            return redirect(redirect_url)

        if nova_senha != '':
            if len(nova_senha) < 8:
                error_message = ('A senha precisa ter pelo menos 8 caracteres.')
                messages.error(request, error_message)
                redirect_url = reverse('EditarColaborador', args=[colaborador_id])
                return redirect(redirect_url)

        if nova_senha and nova_senha != confirma_nova_senha:
            error_message = ('A confirmação da senha fornecida não corresponde com a senha informada.')
            messages.error(request, error_message)
            redirect_url = reverse('EditarColaborador', args=[colaborador_id])
            return redirect(redirect_url)

        if confirma_nova_senha and confirma_nova_senha != nova_senha:
            error_message = ('A confirmação da senha fornecida não corresponde com a senha informada.')
            messages.error(request, error_message)
            redirect_url = reverse('EditarColaborador', args=[colaborador_id])
            return redirect(redirect_url)

        try:
            colaborador.nome = nome
            colaborador.cpf = cpf
            colaborador.login = login

            if nova_senha:
                senha_hash = make_password(nova_senha)
                colaborador.senha = senha_hash
           
            colaborador.save()
            success_message = ('Dados do colaborador atualizados com sucesso!')
            messages.success(request, success_message)
            redirect_url = reverse('EditarColaborador', args=[colaborador_id])
            return redirect(redirect_url)   
             
        except Exception as e:
            print(str(e))
            error_message = ('Ocorreu um erro durante o processo de atualização dos dados do colaborador.')
            messages.error(request, error_message)
            redirect_url = reverse('EditarColaborador', args=[colaborador_id])
            return redirect(redirect_url)

    try:
        colaborador = Colaborador.objects.get(pk=colaborador_id)
        return render (request, 'colaboradores/editar_colaborador.html', {'colaborador': colaborador})
    
    except Exception as e:
        print(str(e))
        error_message = ('Ocorreu um erro ao tentar editar os dados do colaborador.')
        return render (request, 'colaboradores/editar_colaborador.html', {'error_mssage': error_message})