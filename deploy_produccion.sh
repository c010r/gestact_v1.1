#!/bin/bash
# =============================================================================
# Script de despliegue en producción — GestACT
# Servidor: Rocky Linux 9 | Web: Nginx + Gunicorn
# Uso: sudo bash deploy_produccion.sh
# =============================================================================

set -e  # Detener ante cualquier error

# --- Colores ---
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
ok()   { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC}  $1"; }
err()  { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# --- Verificar root ---
[ "$EUID" -ne 0 ] && err "Ejecutar como root: sudo bash $0"

# --- Verificar Rocky Linux ---
[ -f /etc/rocky-release ] || warn "Este script está optimizado para Rocky Linux 9."

# =============================================================================
# CONFIGURACIÓN
# =============================================================================
APP_NAME="gestact"
PROJECT_DIR="/opt/gestact"
REPO_SRC="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"
APP_USER="gestact"
APP_GROUP="nginx"               # Rocky Linux usa el grupo 'nginx'
DJANGO_MODULE="sgai.wsgi"
GUNICORN_WORKERS=3              # workers = (2 × núcleos) + 1 recomendado
GUNICORN_SOCKET="/run/gunicorn_gestact.sock"

echo ""
echo "=============================================="
echo "   Despliegue GestACT en Producción"
echo "   Rocky Linux 9 | Nginx + Gunicorn"
echo "=============================================="
echo ""

# --- Solicitar IP/dominio ---
read -rp "Ingrese la IP o dominio del servidor (ej: 192.168.1.10 o gestact.ejemplo.com): " SERVER_HOST
[ -z "$SERVER_HOST" ] && err "Debe ingresar una IP o dominio."

# --- Generar SECRET_KEY segura ---
SECRET_KEY=$(python3 -c "import secrets, string; \
    chars = string.ascii_letters + string.digits + '!@#\$%^&*(-_=+)'; \
    print(''.join(secrets.choice(chars) for _ in range(60)))")

# =============================================================================
# 1. Dependencias del sistema (dnf)
# =============================================================================
echo ""
ok "Instalando dependencias del sistema con dnf..."
dnf install -y epel-release
dnf install -y python3 python3-pip python3-devel nginx rsync gcc

# python3-venv no existe como paquete separado en Rocky 9,
# pero python3 ya trae el módulo venv incluido.
ok "Dependencias instaladas."

# =============================================================================
# 2. Usuario del sistema
# =============================================================================
if ! id "$APP_USER" &>/dev/null; then
    useradd --system --shell /sbin/nologin \
            --home-dir "$PROJECT_DIR" \
            --gid "$APP_GROUP" \
            "$APP_USER"
    ok "Usuario '$APP_USER' creado."
else
    warn "Usuario '$APP_USER' ya existe, omitiendo."
fi

# =============================================================================
# 3. Copiar proyecto al directorio de producción
# =============================================================================
ok "Copiando proyecto a $PROJECT_DIR..."
mkdir -p "$PROJECT_DIR"
rsync -a --exclude='venv' --exclude='__pycache__' --exclude='*.pyc' \
         --exclude='.git'  --exclude='*.sqlite3' \
         "$REPO_SRC/" "$PROJECT_DIR/"

# =============================================================================
# 4. Entorno virtual + dependencias + gunicorn
# =============================================================================
ok "Configurando entorno virtual..."
python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install --upgrade pip -q
"$VENV_DIR/bin/pip" install -r "$PROJECT_DIR/requirements.txt" -q
"$VENV_DIR/bin/pip" install gunicorn -q
ok "Gunicorn instalado."

# =============================================================================
# 5. Settings de producción
# =============================================================================
ok "Generando settings de producción..."
cat > "$PROJECT_DIR/sgai/settings_production.py" << SETTINGS_EOF
"""
Settings de producción — GestACT
Generado automáticamente por deploy_produccion.sh
"""
from .settings import *

# Seguridad
DEBUG = False
SECRET_KEY = '${SECRET_KEY}'
ALLOWED_HOSTS = ['${SERVER_HOST}', 'www.${SERVER_HOST}']

# Archivos estáticos
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'

# CORS — solo el dominio propio en producción
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    'http://${SERVER_HOST}',
    'http://www.${SERVER_HOST}',
]

# Seguridad de sesión
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = 'DENY'
SETTINGS_EOF
ok "Archivo sgai/settings_production.py creado."

# =============================================================================
# 6. Collectstatic y migraciones
# =============================================================================
ok "Ejecutando collectstatic..."
DJANGO_SETTINGS_MODULE=sgai.settings_production \
    "$VENV_DIR/bin/python" "$PROJECT_DIR/manage.py" collectstatic --noinput -v 0

ok "Ejecutando migraciones..."
DJANGO_SETTINGS_MODULE=sgai.settings_production \
    "$VENV_DIR/bin/python" "$PROJECT_DIR/manage.py" migrate --noinput

# =============================================================================
# 7. Permisos
# =============================================================================
chown -R "$APP_USER:$APP_GROUP" "$PROJECT_DIR"
chmod -R 750 "$PROJECT_DIR"
chmod 664 "$PROJECT_DIR/db.sqlite3" 2>/dev/null || true
# El directorio de la DB necesita escritura para SQLite
chmod 775 "$PROJECT_DIR"
ok "Permisos configurados."

# =============================================================================
# 8. SELinux — permitir a Nginx conectarse al socket Unix
# =============================================================================
ok "Configurando SELinux..."
if command -v getenforce &>/dev/null && [ "$(getenforce)" != "Disabled" ]; then
    # Permitir que nginx se conecte a procesos en red/socket
    setsebool -P httpd_can_network_connect 1

    # Etiquetar el directorio del proyecto para que nginx pueda leer estáticos
    semanage fcontext -a -t httpd_sys_content_t "$PROJECT_DIR/staticfiles(/.*)?" 2>/dev/null || \
    semanage fcontext -m -t httpd_sys_content_t "$PROJECT_DIR/staticfiles(/.*)?"
    restorecon -Rv "$PROJECT_DIR/staticfiles/" 2>/dev/null || true

    # Etiquetar el socket de gunicorn
    semanage fcontext -a -t httpd_var_run_t "${GUNICORN_SOCKET}" 2>/dev/null || true

    ok "SELinux configurado."
else
    warn "SELinux desactivado, omitiendo configuración."
fi

# =============================================================================
# 9. Firewalld — abrir puerto 80
# =============================================================================
ok "Configurando firewall (puerto 80)..."
if systemctl is-active --quiet firewalld; then
    firewall-cmd --permanent --add-service=http
    firewall-cmd --reload
    ok "Puerto 80 abierto en firewalld."
else
    warn "firewalld no está activo, verifique el firewall manualmente."
fi

# =============================================================================
# 10. Servicio systemd — Gunicorn socket
# =============================================================================
ok "Configurando servicio systemd para Gunicorn..."
cat > "/etc/systemd/system/gunicorn_${APP_NAME}.socket" << EOF
[Unit]
Description=Gunicorn socket — ${APP_NAME}

[Socket]
ListenStream=${GUNICORN_SOCKET}
SocketUser=nginx

[Install]
WantedBy=sockets.target
EOF

# =============================================================================
# 11. Servicio systemd — Gunicorn service
# =============================================================================
cat > "/etc/systemd/system/gunicorn_${APP_NAME}.service" << EOF
[Unit]
Description=Gunicorn daemon — ${APP_NAME}
Requires=gunicorn_${APP_NAME}.socket
After=network.target

[Service]
User=${APP_USER}
Group=${APP_GROUP}
WorkingDirectory=${PROJECT_DIR}
Environment="DJANGO_SETTINGS_MODULE=sgai.settings_production"
ExecStart=${VENV_DIR}/bin/gunicorn \\
    --workers ${GUNICORN_WORKERS} \\
    --bind unix:${GUNICORN_SOCKET} \\
    --timeout 120 \\
    --access-logfile /var/log/gunicorn_${APP_NAME}_access.log \\
    --error-logfile  /var/log/gunicorn_${APP_NAME}_error.log \\
    ${DJANGO_MODULE}:application

ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable  "gunicorn_${APP_NAME}.socket"
systemctl restart "gunicorn_${APP_NAME}.socket"
ok "Gunicorn socket activo."

# =============================================================================
# 12. Configuración Nginx
# Rocky Linux usa /etc/nginx/conf.d/ (NO sites-available/sites-enabled)
# proxy_params no existe en Rocky — se declaran inline
# =============================================================================
ok "Configurando Nginx..."
cat > "/etc/nginx/conf.d/${APP_NAME}.conf" << EOF
server {
    listen 80;
    server_name ${SERVER_HOST} www.${SERVER_HOST};

    # Archivos estáticos servidos directamente por Nginx
    location /static/ {
        alias ${PROJECT_DIR}/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Todo lo demás pasa a Gunicorn
    location / {
        proxy_pass          http://unix:${GUNICORN_SOCKET};
        proxy_set_header    Host              \$host;
        proxy_set_header    X-Real-IP         \$remote_addr;
        proxy_set_header    X-Forwarded-For   \$proxy_add_x_forwarded_for;
        proxy_set_header    X-Forwarded-Proto \$scheme;
        proxy_redirect      off;
        proxy_read_timeout  120s;
        proxy_connect_timeout 120s;
    }

    # Seguridad
    server_tokens off;

    # Logs
    access_log /var/log/nginx/${APP_NAME}_access.log;
    error_log  /var/log/nginx/${APP_NAME}_error.log;
}
EOF

# Deshabilitar el virtual host por defecto de Rocky
sed -i 's/^/#/' /etc/nginx/conf.d/default.conf 2>/dev/null || true

nginx -t && systemctl enable nginx && systemctl restart nginx
ok "Nginx configurado y reiniciado."

# =============================================================================
# 13. Iniciar Gunicorn
# =============================================================================
systemctl start  "gunicorn_${APP_NAME}.service"
systemctl enable "gunicorn_${APP_NAME}.service"

# =============================================================================
# Resumen final
# =============================================================================
echo ""
echo "=============================================="
ok "Despliegue completado exitosamente."
echo "=============================================="
echo ""
echo "  URL del sistema : http://${SERVER_HOST}/"
echo "  Proyecto        : ${PROJECT_DIR}"
echo "  Settings prod.  : ${PROJECT_DIR}/sgai/settings_production.py"
echo "  Logs Gunicorn   : /var/log/gunicorn_${APP_NAME}_*.log"
echo "  Logs Nginx      : /var/log/nginx/${APP_NAME}_*.log"
echo ""
echo "  Comandos útiles:"
echo "  ─────────────────────────────────────────────────────"
echo "  Ver estado app  : systemctl status gunicorn_${APP_NAME}"
echo "  Reiniciar app   : systemctl restart gunicorn_${APP_NAME}"
echo "  Recargar Nginx  : systemctl reload nginx"
echo "  Ver logs app    : journalctl -u gunicorn_${APP_NAME} -f"
echo "  Ver logs nginx  : tail -f /var/log/nginx/${APP_NAME}_error.log"
echo "  Estado SELinux  : getenforce"
echo ""
warn "IMPORTANTE: Edite ${PROJECT_DIR}/sgai/settings_production.py"
warn "si necesita ajustar ALLOWED_HOSTS, base de datos u otras opciones."
echo ""
