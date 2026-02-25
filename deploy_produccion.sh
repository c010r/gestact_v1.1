#!/bin/bash
# =============================================================================
# Script de despliegue en producción —  - 2026
# Servidor  : Rocky Linux 9
# Web       : Nginx + Gunicorn
# Base datos: PostgreSQL 15
# Uso       : sudo bash deploy_produccion.sh
# =============================================================================

set -euo pipefail   # Detener ante cualquier error, variable no definida o pipe roto

# --- Colores y helpers -------------------------------------------------------
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
ok()      { echo -e "${GREEN}[OK]${NC}    $1"; }
warn()    { echo -e "${YELLOW}[ ! ]${NC}   $1"; }
err()     { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }
section() { echo -e "\n${CYAN}══════════════════════════════════════════════${NC}"; \
            echo -e "${CYAN}  $1${NC}"; \
            echo -e "${CYAN}══════════════════════════════════════════════${NC}"; }

# --- Verificar root ----------------------------------------------------------
[ "$EUID" -ne 0 ] && err "Ejecutar como root: sudo bash $0"

# --- Verificar Rocky Linux ---------------------------------------------------
[ -f /etc/rocky-release ] || warn "Este script está optimizado para Rocky Linux 9."

# =============================================================================
# CONFIGURACIÓN — ajustar si es necesario
# =============================================================================
APP_NAME="gestact"
PROJECT_DIR="/opt/gestact"
REPO_SRC="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"
APP_USER="gestact"
APP_GROUP="nginx"
DJANGO_MODULE="sgai.wsgi"
GUNICORN_WORKERS=3
GUNICORN_SOCKET="/run/gunicorn_gestact.sock"

# PostgreSQL 15
PG_VERSION="15"
PG_SERVICE="postgresql-${PG_VERSION}"
PG_DATA="/var/lib/pgsql/${PG_VERSION}/data"
PG_SETUP="/usr/pgsql-${PG_VERSION}/bin/postgresql-${PG_VERSION}-setup"
DB_NAME="${APP_NAME}_db"
DB_USER="${APP_NAME}_usr"

# =============================================================================
echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   Despliegue GestACT en Producción           ║${NC}"
echo -e "${CYAN}║   Rocky Linux 9 │ Nginx + Gunicorn + PG15    ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════╝${NC}"
echo ""

# --- Solicitar IP/dominio ----------------------------------------------------
read -rp "  IP o dominio del servidor (ej: 192.168.1.10): " SERVER_HOST
[ -z "$SERVER_HOST" ] && err "Debe ingresar una IP o dominio."

# --- Generar credenciales seguras --------------------------------------------
SECRET_KEY=$(python3 -c "
import secrets, string
chars = string.ascii_letters + string.digits + '!@#\$%^&*(-_=+)'
print(''.join(secrets.choice(chars) for _ in range(64)))
")
DB_PASSWORD=$(python3 -c "
import secrets, string
chars = string.ascii_letters + string.digits + '_-'
print(''.join(secrets.choice(chars) for _ in range(32)))
")

# =============================================================================
section "1. Dependencias del sistema"
# =============================================================================
dnf install -y epel-release

# Python 3.11 — Rocky Linux 9 viene con Python 3.9 por defecto,
# pero Django 5.x requiere Python >= 3.10.
# Python 3.11 está disponible en el AppStream de Rocky Linux 9.
dnf install -y \
    python3.11 python3.11-pip python3.11-devel \
    nginx \
    rsync gcc make \
    policycoreutils-python-utils \
    wget curl

# libpq-devel: necesario para compilar psycopg2 desde fuente.
# Se instala solo si no está presente y deshabilitando repos PGDG
# para evitar el conflicto de dependencia perl(IPC::Run).
if ! rpm -q libpq-devel &>/dev/null; then
    dnf install -y --disablerepo="pgdg*" libpq-devel 2>/dev/null || \
        warn "libpq-devel no pudo instalarse (no requerido si se usa psycopg2-binary)."
else
    ok "libpq-devel ya instalado, saltando."
fi

# Verificar que Python 3.11 quedó instalado
PYTHON311=$(command -v python3.11) || err "No se pudo instalar python3.11. Verifique los repositorios dnf."
PY_VER=$("$PYTHON311" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
ok "Python ${PY_VER} disponible en: ${PYTHON311}"

"$PYTHON311" -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" || \
    err "Python ${PY_VER} es demasiado antiguo para Django 5.x. Se necesita >= 3.10."

ok "Dependencias base instaladas."

# =============================================================================
section "2. Instalación de PostgreSQL ${PG_VERSION}"
# =============================================================================

# Repositorio oficial de PostgreSQL
PG_REPO_RPM="https://download.postgresql.org/pub/repos/yum/reporpms/EL-9-x86_64/pgdg-redhat-repo-latest.noarch.rpm"
if ! rpm -q pgdg-redhat-repo &>/dev/null; then
    dnf install -y "$PG_REPO_RPM"
    ok "Repositorio PostgreSQL PGDG instalado."
else
    ok "Repositorio PostgreSQL PGDG ya estaba instalado."
fi

# Deshabilitar el módulo postgresql del AppStream para evitar conflictos
dnf -qy module disable postgresql 2>/dev/null || true

# Instalar PostgreSQL 15
dnf install -y \
    postgresql${PG_VERSION}-server \
    postgresql${PG_VERSION}-contrib \
    postgresql${PG_VERSION}
ok "PostgreSQL ${PG_VERSION} instalado."

# Inicializar el cluster de base de datos (solo si no fue inicializado antes)
if [ ! -f "${PG_DATA}/PG_VERSION" ]; then
    "$PG_SETUP" initdb
    ok "Cluster de PostgreSQL inicializado."
else
    warn "Cluster ya existe en ${PG_DATA}, omitiendo initdb."
fi

# Habilitar y arrancar PostgreSQL
systemctl enable "$PG_SERVICE"
systemctl start  "$PG_SERVICE"
ok "Servicio ${PG_SERVICE} activo."

# =============================================================================
section "3. Configuración de autenticación PostgreSQL (pg_hba.conf)"
# =============================================================================
PG_HBA="${PG_DATA}/pg_hba.conf"

# Cambiar métodos de autenticación de ident/peer a scram-sha-256 para
# conexiones TCP desde localhost, de modo que Django pueda autenticarse.
python3 << PYHBA
import re

path = '${PG_HBA}'
with open(path) as f:
    content = f.read()

# Cambiar ident → scram-sha-256 en conexiones host (IPv4 e IPv6)
content = re.sub(
    r'^(host\s+all\s+all\s+127\.0\.0\.1/32\s+)\S+',
    r'\1scram-sha-256',
    content, flags=re.MULTILINE
)
content = re.sub(
    r'^(host\s+all\s+all\s+::1/128\s+)\S+',
    r'\1scram-sha-256',
    content, flags=re.MULTILINE
)

# Agregar regla específica para el usuario de la app (al principio)
app_rule = (
    '# GestACT — acceso para usuario de aplicación\n'
    'host    ${DB_NAME}   ${DB_USER}   127.0.0.1/32   scram-sha-256\n'
    'host    ${DB_NAME}   ${DB_USER}   ::1/128         scram-sha-256\n'
)
if '${DB_USER}' not in content:
    # Insertar antes de la primera línea 'host'
    content = re.sub(r'^(host\s)', app_rule + r'\1', content, count=1, flags=re.MULTILINE)

with open(path, 'w') as f:
    f.write(content)
print('pg_hba.conf actualizado')
PYHBA

# Recargar para aplicar cambios de pg_hba
systemctl reload "$PG_SERVICE"
ok "pg_hba.conf configurado."

# =============================================================================
section "4. Creación de base de datos y usuario"
# =============================================================================

# Crear usuario de base de datos
if ! su -c "psql -tAc \"SELECT 1 FROM pg_roles WHERE rolname='${DB_USER}'\"" postgres | grep -q 1; then
    su -c "psql -c \"CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';\"" postgres
    ok "Usuario de base de datos '${DB_USER}' creado."
else
    # Actualizar contraseña en caso de re-deploy
    su -c "psql -c \"ALTER USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';\"" postgres
    warn "Usuario '${DB_USER}' ya existía — contraseña actualizada."
fi

# Crear base de datos
if ! su -c "psql -tAc \"SELECT 1 FROM pg_database WHERE datname='${DB_NAME}'\"" postgres | grep -q 1; then
    su -c "psql -c \"CREATE DATABASE ${DB_NAME} OWNER ${DB_USER} ENCODING 'UTF8' LC_COLLATE 'en_US.UTF-8' LC_CTYPE 'en_US.UTF-8';\"" postgres
    ok "Base de datos '${DB_NAME}' creada."
else
    warn "Base de datos '${DB_NAME}' ya existe, omitiendo creación."
fi

# Otorgar privilegios
su -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};\"" postgres
su -c "psql -d ${DB_NAME} -c \"GRANT ALL ON SCHEMA public TO ${DB_USER};\"" postgres
ok "Privilegios otorgados a '${DB_USER}'."

# =============================================================================
section "5. Usuario del sistema"
# =============================================================================
if ! id "$APP_USER" &>/dev/null; then
    useradd --system --shell /sbin/nologin \
            --home-dir "$PROJECT_DIR" \
            --gid "$APP_GROUP" \
            "$APP_USER"
    ok "Usuario del sistema '${APP_USER}' creado."
else
    warn "Usuario '${APP_USER}' ya existe, omitiendo."
fi

# =============================================================================
section "6. Copiar proyecto al directorio de producción"
# =============================================================================
mkdir -p "$PROJECT_DIR"
rsync -a \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='*.sqlite3' \
    --exclude='.env' \
    "$REPO_SRC/" "$PROJECT_DIR/"
ok "Proyecto copiado a ${PROJECT_DIR}."

# =============================================================================
section "7. Entorno virtual Python + dependencias"
# =============================================================================

# Crear venv con Python 3.11 (garantiza compatibilidad con Django 5.x)
"$PYTHON311" -m venv "$VENV_DIR"

# El venv creado con python3.11 puede no tener el symlink 'python' en algunas
# distribuciones. Usar siempre la ruta explícita python3 dentro del venv.
VENV_PYTHON="$VENV_DIR/bin/python3"
VENV_PIP="$VENV_DIR/bin/pip3"

# Verificar que el python del venv responde
"$VENV_PYTHON" -c "import sys; print('venv python:', sys.executable, sys.version)"

# Actualizar pip
"$VENV_PIP" install --upgrade pip

# Instalar dependencias del proyecto (incluye qrcode, reportlab, pillow, etc.)
# Sin -q para ver errores si los hay
"$VENV_PIP" install -r "$PROJECT_DIR/requirements.txt"

# Instalar psycopg2 (adaptador PostgreSQL para Python)
"$VENV_PIP" install psycopg2-binary

# Instalar Gunicorn
"$VENV_PIP" install gunicorn

# Verificar que Django quedó instalado correctamente
"$VENV_PYTHON" -c "import django; print('Django', django.__version__, 'instalado OK')" || \
    err "Django no quedó instalado en el venv. Revise los errores de pip anteriores."

ok "Entorno virtual configurado con todas las dependencias."

# =============================================================================
section "8. Settings de producción"
# =============================================================================
cat > "$PROJECT_DIR/sgai/settings_production.py" << SETTINGS_EOF
"""
Settings de producción — GestACT
Generado automáticamente por deploy_produccion.sh
NO editar manualmente los valores sensibles; use variables de entorno.
"""
from .settings import *

# ── Seguridad ────────────────────────────────────────────────────────────────
DEBUG = False
SECRET_KEY = '${SECRET_KEY}'
ALLOWED_HOSTS = ['${SERVER_HOST}', 'www.${SERVER_HOST}', 'localhost', '127.0.0.1']

# ── Base de datos — PostgreSQL 15 ─────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE'  : 'django.db.backends.postgresql',
        'NAME'    : '${DB_NAME}',
        'USER'    : '${DB_USER}',
        'PASSWORD': '${DB_PASSWORD}',
        'HOST'    : '127.0.0.1',
        'PORT'    : '5432',
        'CONN_MAX_AGE': 60,
        'OPTIONS' : {
            'connect_timeout': 10,
        },
    }
}

# ── Archivos estáticos ────────────────────────────────────────────────────────
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL  = '/static/'

# ── CORS — solo el dominio propio ─────────────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    'http://${SERVER_HOST}',
    'http://www.${SERVER_HOST}',
]

# ── Seguridad de sesión y cabeceras ───────────────────────────────────────────
SESSION_COOKIE_HTTPONLY  = True
SESSION_COOKIE_SAMESITE  = 'Lax'
CSRF_COOKIE_HTTPONLY     = True
CSRF_COOKIE_SAMESITE     = 'Lax'
X_FRAME_OPTIONS          = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True

# ── Logging ───────────────────────────────────────────────────────────────────
LOGGING = {
    'version'           : 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style' : '{',
        },
    },
    'handlers': {
        'file': {
            'level'    : 'WARNING',
            'class'    : 'logging.FileHandler',
            'filename' : '/var/log/gestact/django.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level'   : 'WARNING',
    },
}
SETTINGS_EOF
ok "Archivo sgai/settings_production.py creado."

# Crear directorio de logs de Django
mkdir -p /var/log/gestact
chown "$APP_USER:$APP_GROUP" /var/log/gestact
chmod 775 /var/log/gestact
ok "Directorio de logs /var/log/gestact creado."

# =============================================================================
section "9. Collectstatic y migraciones"
# =============================================================================
export DJANGO_SETTINGS_MODULE="sgai.settings_production"

ok "Ejecutando collectstatic..."
cd "$PROJECT_DIR"
"$VENV_PYTHON" manage.py collectstatic --noinput -v 0

ok "Ejecutando migraciones..."
"$VENV_PYTHON" manage.py migrate --noinput

ok "Creando grupos de acceso del sistema..."
"$VENV_PYTHON" manage.py crear_grupos

ok "Base de datos migrada y grupos creados."

# =============================================================================
section "10. Permisos del sistema de archivos"
# =============================================================================
chown -R "$APP_USER:$APP_GROUP" "$PROJECT_DIR"
chmod -R 750 "$PROJECT_DIR"
# Nginx necesita leer los archivos estáticos
chmod -R 755 "$PROJECT_DIR/staticfiles"
# Directorio raíz accesible para nginx
chmod 755 "$PROJECT_DIR"
ok "Permisos configurados."

# =============================================================================
section "11. SELinux"
# =============================================================================
if command -v getenforce &>/dev/null && [ "$(getenforce)" != "Disabled" ]; then
    # Nginx → Gunicorn (socket Unix)
    setsebool -P httpd_can_network_connect 1

    # Django → PostgreSQL (localhost TCP)
    setsebool -P httpd_can_network_connect_db 1

    # Estáticos servidos por Nginx
    semanage fcontext -a -t httpd_sys_content_t \
        "${PROJECT_DIR}/staticfiles(/.*)?" 2>/dev/null || \
    semanage fcontext -m -t httpd_sys_content_t \
        "${PROJECT_DIR}/staticfiles(/.*)?"
    restorecon -Rv "${PROJECT_DIR}/staticfiles/" 2>/dev/null || true

    # Socket de Gunicorn
    semanage fcontext -a -t httpd_var_run_t \
        "${GUNICORN_SOCKET}" 2>/dev/null || true

    # Logs de Django
    semanage fcontext -a -t httpd_log_t \
        "/var/log/gestact(/.*)?" 2>/dev/null || \
    semanage fcontext -m -t httpd_log_t \
        "/var/log/gestact(/.*)?" 2>/dev/null || true
    restorecon -Rv /var/log/gestact/ 2>/dev/null || true

    ok "SELinux configurado (httpd_can_network_connect + httpd_can_network_connect_db)."
else
    warn "SELinux desactivado — verifique manualmente si es necesario."
fi

# =============================================================================
section "12. Firewall"
# =============================================================================
if systemctl is-active --quiet firewalld; then
    firewall-cmd --permanent --add-service=http
    firewall-cmd --permanent --add-service=https
    # PostgreSQL NO se expone al exterior; solo acceso local desde la app
    firewall-cmd --reload
    ok "Puertos 80 y 443 abiertos en firewalld."
    ok "PostgreSQL permanece en acceso local únicamente (sin exposición externa)."
else
    warn "firewalld no está activo — verifique el firewall manualmente."
fi

# =============================================================================
section "13. Servicio systemd — Gunicorn socket"
# =============================================================================
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
section "14. Servicio systemd — Gunicorn service"
# =============================================================================
cat > "/etc/systemd/system/gunicorn_${APP_NAME}.service" << EOF
[Unit]
Description=Gunicorn daemon — ${APP_NAME}
Requires=gunicorn_${APP_NAME}.socket
After=network.target ${PG_SERVICE}.service

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
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable  "gunicorn_${APP_NAME}.socket"
systemctl restart "gunicorn_${APP_NAME}.socket"
ok "Gunicorn socket activo."

# =============================================================================
section "15. Configuración Nginx"
# =============================================================================
# Deshabilitar virtual host por defecto de Rocky
sed -i 's/^[^#]/#&/' /etc/nginx/conf.d/default.conf 2>/dev/null || true

cat > "/etc/nginx/conf.d/${APP_NAME}.conf" << EOF
server {
    listen 80;
    server_name ${SERVER_HOST} www.${SERVER_HOST};

    client_max_body_size 20M;

    # Archivos estáticos — servidos directamente por Nginx
    location /static/ {
        alias ${PROJECT_DIR}/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Todo lo demás pasa a Gunicorn
    location / {
        proxy_pass            http://unix:${GUNICORN_SOCKET};
        proxy_set_header Host              \$host;
        proxy_set_header X-Real-IP         \$remote_addr;
        proxy_set_header X-Forwarded-For   \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect       off;
        proxy_read_timeout   120s;
        proxy_connect_timeout 10s;
        proxy_send_timeout   120s;
    }

    # Seguridad
    server_tokens off;
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";

    # Logs
    access_log /var/log/nginx/${APP_NAME}_access.log;
    error_log  /var/log/nginx/${APP_NAME}_error.log;
}
EOF

nginx -t && systemctl enable nginx && systemctl restart nginx
ok "Nginx configurado y reiniciado."

# =============================================================================
section "16. Iniciar Gunicorn"
# =============================================================================
systemctl start  "gunicorn_${APP_NAME}.service"
systemctl enable "gunicorn_${APP_NAME}.service"
ok "Gunicorn iniciado."

# =============================================================================
# Guardar credenciales en archivo protegido
# =============================================================================
CREDS_FILE="/root/.gestact_credentials"
cat > "$CREDS_FILE" << CREDS_EOF
# GestACT — Credenciales de producción
# Generado: $(date '+%d/%m/%Y %H:%M')
# GUARDAR EN LUGAR SEGURO — NO COMPARTIR

SECRET_KEY="${SECRET_KEY}"

DB_NAME="${DB_NAME}"
DB_USER="${DB_USER}"
DB_PASSWORD="${DB_PASSWORD}"
DB_HOST="127.0.0.1"
DB_PORT="5432"
CREDS_EOF
chmod 600 "$CREDS_FILE"
ok "Credenciales guardadas en ${CREDS_FILE} (modo 600, solo root)."

# =============================================================================
# Resumen final
# =============================================================================
echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}  Despliegue completado exitosamente.${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "  URL del sistema    : http://${SERVER_HOST}/"
echo "  Proyecto           : ${PROJECT_DIR}"
echo "  Settings prod.     : ${PROJECT_DIR}/sgai/settings_production.py"
echo "  Credenciales BD    : ${CREDS_FILE}  (solo root)"
echo ""
echo "  Base de datos      : PostgreSQL ${PG_VERSION}"
echo "    Host             : 127.0.0.1:5432"
echo "    Base de datos    : ${DB_NAME}"
echo "    Usuario          : ${DB_USER}"
echo "    Contraseña       : ${DB_PASSWORD}"
echo ""
echo "  Logs:"
echo "    Django           : /var/log/gestact/django.log"
echo "    Gunicorn access  : /var/log/gunicorn_${APP_NAME}_access.log"
echo "    Gunicorn error   : /var/log/gunicorn_${APP_NAME}_error.log"
echo "    Nginx access     : /var/log/nginx/${APP_NAME}_access.log"
echo "    Nginx error      : /var/log/nginx/${APP_NAME}_error.log"
echo ""
echo "  Comandos útiles:"
echo "  ──────────────────────────────────────────────────────────────"
echo "  Ver estado app     : systemctl status gunicorn_${APP_NAME}"
echo "  Reiniciar app      : systemctl restart gunicorn_${APP_NAME}"
echo "  Recargar Nginx     : systemctl reload nginx"
echo "  Ver logs app       : journalctl -u gunicorn_${APP_NAME} -f"
echo "  Conectar a BD      : psql -U ${DB_USER} -h 127.0.0.1 -d ${DB_NAME}"
echo "  Estado PostgreSQL  : systemctl status ${PG_SERVICE}"
echo "  Estado SELinux     : getenforce"
echo ""
echo -e "${YELLOW}  IMPORTANTE:${NC}"
echo "  - Las credenciales de BD están en: ${CREDS_FILE}"
echo "  - Para crear usuarios del sistema ejecutar:"
echo "    cd ${PROJECT_DIR} && DJANGO_SETTINGS_MODULE=sgai.settings_production \\"
echo "    ${VENV_DIR}/bin/python manage.py shell"
echo ""
