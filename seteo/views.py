from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import connection
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
import json
import requests
import subprocess
import os
import threading
from .models import ConfiguracionSistema, Usuario, Rol
from inventario.models import Lugares
from .serializers import (
    ConfiguracionSistemaSerializer,
    UsuarioSerializer,
    RolSerializer,
    CambiarPasswordSerializer,
    UsuarioCreateSerializer,
)


# ============================================================================
# VISTAS WEB
# ============================================================================

@login_required
def dashboard(request):
    """Dashboard principal de seteo"""
    context = {
        'total_usuarios': Usuario.objects.count(),
        'usuarios_activos': Usuario.objects.filter(estado='activo').count(),
        'total_roles': Rol.objects.count(),
        'total_configuraciones': ConfiguracionSistema.objects.count(),
        'configuraciones_activas': ConfiguracionSistema.objects.filter(
            activo=True,
        ).count(),
    }
    return render(request, 'seteo/dashboard.html', context)


@login_required
def configuracion_sistema(request):
    """Vista para configuración general del sistema"""
    configuraciones = ConfiguracionSistema.objects.filter(tipo='general')
    
    if request.method == 'POST':
        # Procesar formulario de configuración
        for config in configuraciones:
            nuevo_valor = request.POST.get(f'config_{config.id}')
            if nuevo_valor:
                try:
                    config.valor = json.loads(nuevo_valor)
                    config.save()
                    messages.success(
                        request,
                        f'Configuración {config.nombre} actualizada.',
                    )
                except json.JSONDecodeError:
                    messages.error(
                        request,
                        f'Error en formato JSON para {config.nombre}.',
                    )
    
    return render(request, 'seteo/configuracion_sistema.html', {
        'configuraciones': configuraciones
    })


def configuracion_ubicaciones(request):
    """Panel principal para gestionar ubicaciones jerárquicas."""

    ubicaciones_count = Lugares.objects.count()
    return render(
        request,
        'seteo/configuracion_ubicaciones.html',
        {
            'total_ubicaciones': ubicaciones_count,
        },
    )


def actualizar_configuracion_bd_settings(config_bd):
    """Actualiza settings.DATABASES en caliente para la conexión principal."""
    from django.conf import settings
    import os
    
    # Obtener configuración actual como base
    config_actual = settings.DATABASES['default'].copy()
    
    # Construir la nueva configuración manteniendo campos requeridos
    nueva_config = {
        'ENGINE': config_bd.valor.get('engine', 'django.db.backends.sqlite3'),
        'ATOMIC_REQUESTS': config_actual.get('ATOMIC_REQUESTS', False),
        'AUTOCOMMIT': config_actual.get('AUTOCOMMIT', True),
        'CONN_MAX_AGE': config_actual.get('CONN_MAX_AGE', 0),
        'CONN_HEALTH_CHECKS': config_actual.get('CONN_HEALTH_CHECKS', False),
        'OPTIONS': config_actual.get('OPTIONS', {}),
        'TIME_ZONE': config_actual.get('TIME_ZONE', None),
        'TEST': config_actual.get('TEST', {}),
    }
    
    # Configurar según el tipo de motor de BD
    if 'sqlite' in nueva_config['ENGINE']:
        # Para SQLite, usar ruta absoluta
        db_name = config_bd.valor.get('name', 'db.sqlite3')
        if not os.path.isabs(db_name):
            nueva_config['NAME'] = settings.BASE_DIR / db_name
        else:
            nueva_config['NAME'] = db_name
    else:
        # Para otras BD (PostgreSQL, MySQL, etc.)
        nueva_config.update({
            'NAME': config_bd.valor.get('name', ''),
            'HOST': config_bd.valor.get('host', ''),
            'PORT': config_bd.valor.get('port', ''),
            'USER': config_bd.valor.get('user', ''),
            'PASSWORD': config_bd.valor.get('password', ''),
        })
    
    # Actualizar la configuración de Django en tiempo de ejecución
    settings.DATABASES['default'] = nueva_config
    
    # Cerrar conexiones existentes para forzar reconexión
    from django.db import connections
    connections.close_all()


@login_required
def configuracion_bd(request):
    """Vista para configurar las credenciales de base de datos."""
    config_bd, created = ConfiguracionSistema.objects.get_or_create(
        nombre='database_config',
        tipo='database',
        defaults={
            'descripcion': 'Configuración de conexión a base de datos',
            'valor': {
                'engine': 'django.db.backends.sqlite3',
                'name': 'db.sqlite3',
                'host': '',
                'port': '',
                'user': '',
                'password': ''
            }
        }
    )
    
    if request.method == 'POST':
        nuevo_valor = {
            'engine': request.POST.get('engine', ''),
            'name': request.POST.get('name', ''),
            'host': request.POST.get('host', ''),
            'port': request.POST.get('port', ''),
            'user': request.POST.get('user', ''),
            'password': request.POST.get('password', '')
        }
        
        # Validar configuración antes de guardar
        try:
            # Guardar configuración actual
            config_bd.valor = nuevo_valor
            config_bd.save()
            
            # Aplicar la nueva configuración
            actualizar_configuracion_bd_settings(config_bd)
            
            # Probar conexión
            try:
                connection.ensure_connection()
                messages.success(
                    request,
                    'Configuración guardada y conexión verificada.',
                )
            except Exception as e:
                messages.warning(
                    request,
                    'Guardado con éxito, pero la conexión falló: %s' % e,
                )
                
        except Exception as e:
            messages.error(
                request,
                'Error al actualizar la configuración: %s' % e,
            )
            
        return redirect('seteo:configuracion_bd')
    
    return render(request, 'seteo/configuracion_bd.html', {
        'config': config_bd
    })


@login_required
def configuracion_keycloak(request):
    """Vista para configuración de Keycloak"""
    config_keycloak, created = ConfiguracionSistema.objects.get_or_create(
        nombre='keycloak_config',
        tipo='keycloak',
        defaults={
            'descripcion': 'Configuración de conexión a Keycloak',
            'valor': {
                'server_url': '',
                'realm': '',
                'client_id': '',
                'client_secret': '',
                'admin_username': '',
                'admin_password': ''
            }
        }
    )
    
    if request.method == 'POST':
        nuevo_valor = {
            'server_url': request.POST.get('server_url', ''),
            'realm': request.POST.get('realm', ''),
            'client_id': request.POST.get('client_id', ''),
            'client_secret': request.POST.get('client_secret', ''),
            'admin_username': request.POST.get('admin_username', ''),
            'admin_password': request.POST.get('admin_password', '')
        }
        config_keycloak.valor = nuevo_valor
        config_keycloak.save()
        messages.success(request, 'Configuración de Keycloak actualizada')
        return redirect('seteo:configuracion_keycloak')
    
    return render(request, 'seteo/configuracion_keycloak.html', {
        'config': config_keycloak
    })


@login_required
def gestion_usuarios(request):
    """Vista para gestión de usuarios"""
    usuarios_list = Usuario.objects.all().order_by('username')
    paginator = Paginator(usuarios_list, 20)
    page_number = request.GET.get('page')
    usuarios = paginator.get_page(page_number)
    
    roles = Rol.objects.filter(activo=True)
    
    return render(request, 'seteo/gestion_usuarios.html', {
        'usuarios': usuarios,
        'roles': roles
    })


@login_required
def gestion_roles(request):
    """Vista para gestión de roles"""
    roles_list = Rol.objects.all().order_by('nombre')
    paginator = Paginator(roles_list, 20)
    page_number = request.GET.get('page')
    roles = paginator.get_page(page_number)
    
    return render(request, 'seteo/gestion_roles.html', {
        'roles': roles
    })


@login_required
def crear_bd_form(request):
    """Vista para mostrar el formulario de creación de base de datos"""
    return render(request, 'seteo/crear_bd_form.html')


# ============================================================================
# API VIEWS
# ============================================================================

class ConfiguracionViewSet(viewsets.ModelViewSet):
    """ViewSet para ConfiguracionSistema"""
    queryset = ConfiguracionSistema.objects.all()
    serializer_class = ConfiguracionSistemaSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        tipo = self.request.query_params.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        return queryset
    
    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        """Activar configuración"""
        config = self.get_object()
        config.activo = True
        config.save()
        return Response({'status': 'Configuración activada'})
    
    @action(detail=True, methods=['post'])
    def desactivar(self, request, pk=None):
        """Desactivar configuración"""
        config = self.get_object()
        config.activo = False
        config.save()
        return Response({'status': 'Configuración desactivada'})


class UsuarioViewSet(viewsets.ModelViewSet):
    """ViewSet para Usuario"""
    queryset = Usuario.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UsuarioCreateSerializer
        return UsuarioSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        estado = self.request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        return queryset
    
    @action(detail=True, methods=['post'])
    def cambiar_password(self, request, pk=None):
        """Cambiar contraseña de usuario"""
        usuario = self.get_object()
        serializer = CambiarPasswordSerializer(
            data=request.data,
            context={'request': request},
        )
        
        if serializer.is_valid():
            usuario.set_password(serializer.validated_data['password_nueva'])
            usuario.save()
            return Response({'status': 'Contraseña cambiada exitosamente'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        """Activar usuario"""
        usuario = self.get_object()
        usuario.estado = 'activo'
        usuario.is_active = True
        usuario.save()
        return Response({'status': 'Usuario activado'})
    
    @action(detail=True, methods=['post'])
    def desactivar(self, request, pk=None):
        """Desactivar usuario"""
        usuario = self.get_object()
        usuario.estado = 'inactivo'
        usuario.is_active = False
        usuario.save()
        return Response({'status': 'Usuario desactivado'})


class RolViewSet(viewsets.ModelViewSet):
    """ViewSet para Rol"""
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        """Activar rol"""
        rol = self.get_object()
        rol.activo = True
        rol.save()
        return Response({'status': 'Rol activado'})
    
    @action(detail=True, methods=['post'])
    def desactivar(self, request, pk=None):
        """Desactivar rol"""
        rol = self.get_object()
        rol.activo = False
        rol.save()
        return Response({'status': 'Rol desactivado'})


# ============================================================================
# API ENDPOINTS ESPECÍFICOS
# ============================================================================

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def test_conexion_bd(request):
    """Probar conexión a base de datos"""
    try:
        # Aquí se podría implementar la lógica para probar la conexión
        # con los parámetros proporcionados
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        
        return Response({
            'success': True,
            'message': 'Conexión exitosa a la base de datos'
        })
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error de conexión: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def test_conexion_keycloak(request):
    """Probar conexión a Keycloak"""
    try:
        config_data = request.data
        server_url = config_data.get('server_url')
        realm = config_data.get('realm')
        
        if not server_url or not realm:
            return Response({
                'success': False,
                'message': 'URL del servidor y realm son requeridos'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Probar conexión a Keycloak
        test_url = f"{server_url}/realms/{realm}"
        response = requests.get(test_url, timeout=10)
        
        if response.status_code == 200:
            return Response({
                'success': True,
                'message': 'Conexión exitosa a Keycloak'
            })
        else:
            return Response({
                'success': False,
                'message': f'Error de conexión: HTTP {response.status_code}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    except requests.exceptions.RequestException as e:
        return Response({
            'success': False,
            'message': f'Error de conexión: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error inesperado: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def ejecutar_script_bd(request):
    """Ejecuta el script automatizado de creación de base de datos."""
    try:
        data = request.data
        motor = data.get('motor', 'sqlite')
        
        # Validar motor
        motores_validos = ['sqlite', 'postgresql', 'mysql', 'oracle']
        if motor not in motores_validos:
            return Response({
                'success': False,
                'message': (
                    'Motor no válido. Debe ser uno de: %s'
                    % ', '.join(motores_validos)
                ),
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Preparar parámetros según el motor
        params = {
            'nombre': data.get(
                'nombre',
                'db.sqlite3' if motor == 'sqlite' else 'asse_gestit_db',
            ),
        }
        
        if motor != 'sqlite':
            params.update({
                'host': data.get('host', 'localhost'),
                'puerto': data.get(
                    'puerto',
                    '5432' if motor == 'postgresql'
                    else '3306' if motor == 'mysql'
                    else '1521',
                ),
                'usuario': data.get('usuario', 'asse_gestit_user'),
                'password': data.get('password', 'asse_gestit_password')
            })
        
        # Crear archivo temporal con parámetros
        import tempfile

        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.json',
            delete=False,
        ) as f:
            json.dump(params, f)
            params_file = f.name
        
        # Ejecutar script automatizado en hilo separado
        logs = []
        success = False
        
        def ejecutar_script():
            nonlocal logs, success
            try:
                # Cambiar al directorio del proyecto
                project_dir = os.path.dirname(
                    os.path.dirname(os.path.abspath(__file__))
                )
                
                # Comando para ejecutar el script automatizado
                cmd = [
                    'python', 'crear_bd_automatico.py',
                    '--motor', motor,
                    '--params-file', params_file
                ]
                
                # Ejecutar el comando
                process = subprocess.Popen(
                    cmd,
                    cwd=project_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                # Leer salida línea por línea
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        line = output.strip()
                        if line:
                            # Determinar tipo de log basado en iconos
                            log_type = 'info'
                            if '✅' in line:
                                log_type = 'success'
                            elif '⚠️' in line:
                                log_type = 'warning'
                            elif '❌' in line:
                                log_type = 'error'
                            elif '🔄' in line:
                                log_type = 'process'
                            
                            logs.append({
                                'message': line,
                                'type': log_type
                            })
                
                # Esperar a que termine el proceso
                process.wait()
                success = process.returncode == 0
                
                if not success and not logs:
                    logs.append({
                        'message': 'El script terminó con errores',
                        'type': 'error'
                    })
                
            except subprocess.TimeoutExpired:
                logs.append({
                    'message': 'Timeout: el script tardó demasiado.',
                    'type': 'error',
                })
            except Exception as e:
                logs.append({
                    'message': f'Error al ejecutar script: {str(e)}',
                    'type': 'error',
                })
            finally:
                # Limpiar archivo temporal
                try:
                    os.unlink(params_file)
                except OSError:
                    pass
        
        # Ejecutar en hilo separado para no bloquear la respuesta
        thread = threading.Thread(target=ejecutar_script)
        thread.start()
        thread.join(timeout=120)  # Timeout de 2 minutos
        
        if thread.is_alive():
            return Response({
                'success': False,
                'message': 'El script tardó demasiado en ejecutarse (timeout)',
                'logs': logs
            }, status=status.HTTP_408_REQUEST_TIMEOUT)
        
        return Response({
            'success': success,
            'message': (
                'Script ejecutado correctamente'
                if success
                else 'Error al ejecutar script'
            ),
            'logs': logs,
            'motor': motor
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error interno: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
