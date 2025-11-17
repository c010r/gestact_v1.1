from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.urls import reverse


def get_user_dashboard_url(user):
    """Determinar URL del dashboard según el grupo del usuario"""
    if user.groups.filter(name='Activos Informáticos').exists():
        return reverse('inventario:dashboard_informatica')
    elif user.groups.filter(name='Tecnología Médica').exists():
        return reverse('inventario:dashboard_medica')
    else:
        # Usuario sin grupo específico, dashboard selector
        return reverse('inventario:dashboard')


def login_view(request):
    """Vista personalizada de login"""
    if request.user.is_authenticated:
        # Redirigir al dashboard correspondiente si ya está autenticado
        return redirect(get_user_dashboard_url(request.user))
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Obtener URL de destino según el grupo del usuario
                next_url = request.GET.get('next')
                if not next_url:
                    next_url = get_user_dashboard_url(user)
                
                grupo_usuario = user.groups.first()
                grupo_nombre = grupo_usuario.name if grupo_usuario else "General"
                messages.success(request, f'Bienvenido, {user.get_full_name() or user.username}! ({grupo_nombre})')
                return redirect(next_url)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    """Vista personalizada de logout"""
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('auth:login')