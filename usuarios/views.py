from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import TemplateView
from django.contrib import messages



class FormularioView(UserPassesTestMixin, TemplateView):
    template_name = 'cadastro_usuario.html'

    def test_func(self):
        return self.request.user.is_superuser
    

def is_superuser(user):
    return user.is_superuser    


@csrf_protect
def Login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request,user)
                return redirect('DashBoard')
            else:
                request.session['form_data'] = {'username': username}
                error_message = ('Nome de usuário ou senha inválidos.')
                messages.error(request, error_message)
                return redirect ('Login')

        except Exception as e:
            print(str(e))
            request.session['form_data'] = {'username': username}
            error_message = ('Ocorreu um erro durante o processo de login.')
            messages.error(request, error_message)
            return redirect ('Login')
    
    if request.user.is_authenticated:
        return redirect ('DashBoard')

    form_data = request.session.get('form_data', {})
    request.session['form_data'] = {}
    return render(request, 'usuarios/login.html', {'form_data': form_data})    


@login_required(login_url='Login')
@user_passes_test(is_superuser)
def Usuarios(request):
    try:
        usuarios = User.objects.filter(is_superuser=False)
        return render(request, 'usuarios/usuarios.html', {'usuarios': usuarios})

    except Exception as e:
        print(str(e))
        error_message = ('Ocorreu um erro ao listar os usuários.')
        return render(request, 'usuarios/usuarios.html', {'error_message': error_message})


@csrf_protect
@login_required(login_url='Login')
@user_passes_test(is_superuser)
def CadastroUsuario(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not username.strip():
            request.session['form_data'] = {'username': username, 'email': email}
            error_message = 'O campo username não pode ser vazio.'
            messages.error(request, error_message)
            return redirect ('CadastroUsuario')

        if User.objects.filter(username=username).exists():
            request.session['form_data'] = {'username': username, 'email': email}
            error_message = ('Nome de usuário já cadastrado.')
            messages.error(request, error_message)
            return redirect ('CadastroUsuario')

        if User.objects.filter(email=email).exists():
            request.session['form_data'] = {'username': username, 'email': email}
            error_message = ('Email já cadastrado')
            messages.error(request, error_message)
            return redirect ('CadastroUsuario')

        if password != confirm_password:
            request.session['form_data'] = {'username': username, 'email': email}
            error_message = ('A confirmação da senha fornecida não corresponde com a senha informada.')
            messages.error(request, error_message)
            return redirect ('CadastroUsuario')        

        try:
            validate_password(password)
            User.objects.create_user(username=username, email=email, password=password)
            request.session['form_data'] = {'username': username, 'email': email}
            success_message = ('Usuário cadastrado com sucesso!')
            messages.success(request, success_message)
            return redirect ('CadastroUsuario')
        
        except Exception as e:
            print(str(e))
            request.session['form_data'] = {'username': username, 'email': email}
            error_message = ('A senha não pode muito curta, deve conter pelo menos 8 caracteres, não pode ser muito comum e não pode ser totalmente numérica.')
            messages.error(request, error_message)
            return redirect ('CadastroUsuario')
        
    form_data = request.session.get('form_data', {})
    request.session['form_data'] = {}
    return render(request, 'usuarios/cadastro_usuario.html', {'form_data': form_data})


# @login_required(login_url='Login')
# @user_passes_test(is_superuser)
# def EditarUsuario(request, usuario_id):
#     try:
#         usuario = User.objects.get(pk=usuario_id)      
#         return render (request, 'usuarios/editar_usuario.html', {'usuario': usuario})

#     except Exception as e:
#         print(str(e))
#         error_message = ('Ocorreu um erro ao tentar editar os dados do usuário.')
#         return render (request, 'usuarios/editar_usuario.html', {'error_message': error_message})


@csrf_protect
@login_required(login_url='Login')
@user_passes_test(is_superuser)
def EditarUsuario(request, usuario_id):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not username.strip():
            error_message = 'O campo username não pode ser vazio.'
            messages.error(request, error_message)
            redirect_url = reverse('EditarUsuario', args=[usuario_id])
            return redirect(redirect_url)

        if User.objects.exclude(pk=usuario_id).filter(username=username).exists():
            error_message = ('Nome de usuário já cadastrado.')
            messages.error(request, error_message)
            redirect_url = reverse('EditarUsuario', args=[usuario_id])
            return redirect(redirect_url)

        if User.objects.exclude(pk=usuario_id).filter(email=email).exists():
            error_message = ('Email já cadastrado.')
            messages.error(request, error_message)
            redirect_url = reverse('EditarUsuario', args=[usuario_id])
            return redirect(redirect_url)
        
        if new_password and new_password != confirm_password:
            error_message = ('A confirmação da senha fornecida não corresponde com a senha informada.')
            messages.error(request, error_message)
            redirect_url = reverse('EditarUsuario', args=[usuario_id])
            return redirect(redirect_url)
        
        if confirm_password and confirm_password != new_password:
            error_message = ('A confirmação da senha fornecida não corresponde com a senha informada.')
            messages.error(request, error_message)
            redirect_url = reverse('EditarUsuario', args=[usuario_id])
            return redirect(redirect_url)

        try:
            usuario.username = username
            usuario.email = email

            if new_password:
                validate_password(new_password)
                usuario.set_password(new_password)
           
            usuario.save()
            success_message = ('Dados do usuário atualizados com sucesso!')
            messages.success(request, success_message)
            redirect_url = reverse('EditarUsuario', args=[usuario_id])
            return redirect(redirect_url)
        
        except Exception as e:
            print(str(e))
            error_message = ('A senha não pode muito curta, deve conter pelo menos 8 caracteres, não pode ser muito comum e não pode ser totalmente numérica.')
            messages.error(request, error_message)
            redirect_url = reverse('EditarUsuario', args=[usuario_id])
            return redirect(redirect_url)

    try:
        usuario = User.objects.get(pk=usuario_id)
        return render (request, 'usuarios/editar_usuario.html', {'usuario': usuario})

    except Exception as e:
        print(str(e)) 
        error_message = ('Ocorreu um erro ao tentar editar os dados do usuário.')
        return render (request, 'usuarios/editar_usuario.html', {'error_message': error_message})


@csrf_protect
@login_required(login_url='Login')
@user_passes_test(is_superuser)
def ExcluirUsuario(request, usuario_id):
    try:
        usuario = get_object_or_404(User, pk=usuario_id)

        if request.method == 'POST':
            usuario.delete()
            return redirect('Usuarios')
        
        return render(request, 'usuarios/usuarios.html', {'usuarios': User.objects.all()})
    
    except Exception as e:
        print(e)
        error_message = ('Ocorreu um erro ao excluir o usuário.')
        return render(request, 'usuarios/usuarios.html', {'error_message': error_message})
       

@login_required(login_url='Login')   
def Logout(request):
    logout(request)
    return redirect('Login')