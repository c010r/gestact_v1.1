#!/bin/bash
# =============================================================================
# Setup inicial — GestACT
# Genera el .env con configuración de BD y crea usuarios por rol.
# Uso: bash setup_inicial.sh
# =============================================================================

set -e

# --- Colores ---
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'
ok()     { echo -e "${GREEN}[OK]${NC} $1"; }
warn()   { echo -e "${YELLOW}[!]${NC}  $1"; }
err()    { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }
titulo() { echo -e "\n${BOLD}${CYAN}$1${NC}"; echo "──────────────────────────────────────────"; }
campo()  { echo -e "  ${BOLD}$1${NC}"; }

# --- Detectar directorio del script ---
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_PYTHON="$SCRIPT_DIR/venv/bin/python"
ENV_FILE="$SCRIPT_DIR/.env"
SETTINGS_PROD="$SCRIPT_DIR/sgai/settings_production.py"

[ -f "$VENV_PYTHON" ] || err "Entorno virtual no encontrado. Ejecute primero: python3 -m venv venv && pip install -r requirements.txt"

# --- Leer campo obligatorio (no acepta vacío) ---
leer_requerido() {
    local prompt="$1"
    local valor
    while true; do
        read -rp "  $prompt: " valor
        [ -n "$valor" ] && break
        warn "Este campo es obligatorio."
    done
    echo "$valor"
}

# --- Leer campo opcional ---
leer_opcional() {
    local prompt="$1"
    local valor
    read -rp "  $prompt (opcional): " valor
    echo "$valor"
}

# --- Leer contraseña (oculta, con confirmación) ---
leer_password() {
    local label="$1"
    local pass1 pass2
    while true; do
        read -rsp "  Contraseña para $label: " pass1; echo ""
        [ -z "$pass1" ] && warn "La contraseña no puede estar vacía." && continue
        read -rsp "  Confirmar contraseña:    " pass2; echo ""
        [ "$pass1" = "$pass2" ] && break
        warn "Las contraseñas no coinciden, intente de nuevo."
    done
    echo "$pass1"
}

# --- Generar SECRET_KEY ---
generar_secret_key() {
    python3 -c "import secrets, string; \
        chars = string.ascii_letters + string.digits + '!@#\$%^&*(-_=+)'; \
        print(''.join(secrets.choice(chars) for _ in range(60)))"
}

clear
echo ""
echo "  ╔═══════════════════════════════════════════╗"
echo "  ║       GestACT — Configuración Inicial     ║"
echo "  ╚═══════════════════════════════════════════╝"
echo ""
echo "  Este script configura:"
echo "  1. Conexión a base de datos (.env)"
echo "  2. Usuarios y contraseñas por rol del sistema"
echo ""

# =============================================================================
# SECCIÓN 1 — Base de datos
# =============================================================================
titulo "1. Configuración de Base de Datos"

campo "Motor de base de datos:"
echo "  1) SQLite     (archivo local)"
echo "  2) PostgreSQL (servidor externo)"
echo ""
read -rp "  Seleccione [1/2]: " DB_CHOICE

case "$DB_CHOICE" in
    2)
        DB_ENGINE="postgresql"
        campo "\nDatos de conexión PostgreSQL:"
        DB_HOST=$(leer_requerido "Host del servidor de BD")
        DB_PORT=$(leer_requerido "Puerto")
        DB_NAME=$(leer_requerido "Nombre de la base de datos")
        DB_USER=$(leer_requerido "Usuario de la base de datos")
        DB_PASS=$(leer_password  "la base de datos ($DB_USER)")
        ok "PostgreSQL configurado: $DB_USER@$DB_HOST:$DB_PORT/$DB_NAME"
        ;;
    *)
        DB_ENGINE="sqlite3"
        DB_HOST=""; DB_PORT=""; DB_USER=""; DB_PASS=""
        DB_NAME=$(leer_requerido "Nombre del archivo de base de datos (ej: db.sqlite3)")
        ok "SQLite configurado — archivo: $DB_NAME"
        ;;
esac

# =============================================================================
# SECCIÓN 2 — Datos del servidor
# =============================================================================
titulo "2. Configuración del Servidor"

SERVER_HOST=$(leer_requerido "IP o dominio del servidor")
SECRET_KEY=$(generar_secret_key)
ok "SECRET_KEY generada automáticamente."

# =============================================================================
# SECCIÓN 3 — Usuario Administrador principal (superusuario)
# =============================================================================
titulo "3. Usuario Administrador Principal"

warn "Acceso completo a todos los módulos del sistema."
echo ""
ADMIN_USERNAME=$(leer_requerido "Nombre de usuario")
ADMIN_EMAIL=$(leer_opcional     "Email")
ADMIN_FIRST=$(leer_requerido    "Nombre")
ADMIN_LAST=$(leer_requerido     "Apellido")
ADMIN_PASS=$(leer_password      "$ADMIN_USERNAME")

# =============================================================================
# SECCIÓN 4 — Usuarios por subsistema
# =============================================================================
titulo "4. Usuarios por Subsistema"
echo ""
warn "Puede omitir un módulo respondiendo 'n'."
echo ""

# --- Activos Informáticos ---
campo "[ Activos Informáticos — TI ]"
echo "  Acceso: computadoras, impresoras, monitores, networking,"
echo "          telefonía, periféricos, software e insumos."
echo ""
read -rp "  ¿Crear usuario para este módulo? [S/n]: " CREAR_INF
if [[ "${CREAR_INF,,}" != "n" ]]; then
    INF_USERNAME=$(leer_requerido "Nombre de usuario")
    INF_EMAIL=$(leer_opcional     "Email")
    INF_FIRST=$(leer_requerido    "Nombre")
    INF_LAST=$(leer_requerido     "Apellido")
    INF_PASS=$(leer_password      "$INF_USERNAME")
else
    INF_USERNAME=""
fi
echo ""

# --- Tecnología Médica ---
campo "[ Tecnología Médica ]"
echo "  Acceso: gestión de equipos de tecnología médica."
echo ""
read -rp "  ¿Crear usuario para este módulo? [S/n]: " CREAR_MED
if [[ "${CREAR_MED,,}" != "n" ]]; then
    MED_USERNAME=$(leer_requerido "Nombre de usuario")
    MED_EMAIL=$(leer_opcional     "Email")
    MED_FIRST=$(leer_requerido    "Nombre")
    MED_LAST=$(leer_requerido     "Apellido")
    MED_PASS=$(leer_password      "$MED_USERNAME")
else
    MED_USERNAME=""
fi
echo ""

# --- Activos Generales ---
campo "[ Activos Generales ]"
echo "  Acceso: mobiliario, vehículos y herramientas."
echo ""
read -rp "  ¿Crear usuario para este módulo? [S/n]: " CREAR_GEN
if [[ "${CREAR_GEN,,}" != "n" ]]; then
    GEN_USERNAME=$(leer_requerido "Nombre de usuario")
    GEN_EMAIL=$(leer_opcional     "Email")
    GEN_FIRST=$(leer_requerido    "Nombre")
    GEN_LAST=$(leer_requerido     "Apellido")
    GEN_PASS=$(leer_password      "$GEN_USERNAME")
else
    GEN_USERNAME=""
fi

# =============================================================================
# RESUMEN antes de aplicar
# =============================================================================
titulo "Resumen de configuración"
echo ""
echo "  Base de datos : $DB_ENGINE"
[ "$DB_ENGINE" = "postgresql" ] && echo "  Conexión BD   : $DB_USER@$DB_HOST:$DB_PORT/$DB_NAME"
[ "$DB_ENGINE" = "sqlite3"    ] && echo "  Archivo BD    : $DB_NAME"
echo "  Servidor      : $SERVER_HOST"
echo ""
echo "  Usuarios a crear:"
echo "    [Administrador]        $ADMIN_FIRST $ADMIN_LAST  ($ADMIN_USERNAME)"
[ -n "$INF_USERNAME" ] && echo "    [Activos Informáticos] $INF_FIRST $INF_LAST  ($INF_USERNAME)"
[ -n "$MED_USERNAME" ] && echo "    [Tecnología Médica]    $MED_FIRST $MED_LAST  ($MED_USERNAME)"
[ -n "$GEN_USERNAME" ] && echo "    [Activos Generales]    $GEN_FIRST $GEN_LAST  ($GEN_USERNAME)"
echo ""
read -rp "  ¿Confirmar y aplicar? [S/n]: " CONFIRMAR
[[ "${CONFIRMAR,,}" == "n" ]] && { echo "Cancelado."; exit 0; }

# =============================================================================
# APLICAR — Generar .env
# =============================================================================
titulo "Generando .env..."

cat > "$ENV_FILE" << ENV_EOF
# ================================================================
# GestACT — Variables de entorno
# Generado por setup_inicial.sh — $(date '+%d/%m/%Y %H:%M')
# IMPORTANTE: No versionar este archivo (.gitignore)
# ================================================================

# Seguridad
SECRET_KEY=${SECRET_KEY}
DEBUG=False

# Servidor
ALLOWED_HOSTS=${SERVER_HOST},www.${SERVER_HOST}

# Base de datos
DB_ENGINE=${DB_ENGINE}
DB_NAME=${DB_NAME}
DB_HOST=${DB_HOST}
DB_PORT=${DB_PORT}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASS}
ENV_EOF

ok ".env generado en $ENV_FILE"

# Agregar .env al .gitignore si no está
GITIGNORE="$SCRIPT_DIR/.gitignore"
if [ -f "$GITIGNORE" ]; then
    grep -qx ".env" "$GITIGNORE" || echo ".env" >> "$GITIGNORE"
else
    echo ".env" > "$GITIGNORE"
fi

# =============================================================================
# APLICAR — settings_production.py que lee desde .env
# =============================================================================
titulo "Actualizando settings de producción..."

"$VENV_PYTHON" -c "import dotenv" 2>/dev/null || \
    "$SCRIPT_DIR/venv/bin/pip" install python-dotenv -q

cat > "$SETTINGS_PROD" << SETTINGS_EOF
"""
Settings de producción — GestACT
Generado por setup_inicial.sh — $(date '+%d/%m/%Y %H:%M')
Lee configuración desde el archivo .env del proyecto.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from .settings import *

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

# Seguridad
DEBUG = False
SECRET_KEY = os.environ['SECRET_KEY']
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Base de datos
_DB_ENGINE = os.environ.get('DB_ENGINE', 'sqlite3')

if _DB_ENGINE == 'postgresql':
    DATABASES = {
        'default': {
            'ENGINE':   'django.db.backends.postgresql',
            'NAME':     os.environ.get('DB_NAME', ''),
            'USER':     os.environ.get('DB_USER', ''),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST':     os.environ.get('DB_HOST', 'localhost'),
            'PORT':     os.environ.get('DB_PORT', '5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / os.environ.get('DB_NAME', 'db.sqlite3'),
        }
    }

# Archivos estáticos
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'

# CORS restringido al dominio propio
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    f'http://{h.strip()}'
    for h in os.environ.get('ALLOWED_HOSTS', '').split(',')
    if h.strip()
]

# Seguridad de sesión
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = 'DENY'
SETTINGS_EOF

ok "settings_production.py actualizado."

# =============================================================================
# APLICAR — psycopg2 si es PostgreSQL
# =============================================================================
if [ "$DB_ENGINE" = "postgresql" ]; then
    ok "Instalando psycopg2 para PostgreSQL..."
    "$SCRIPT_DIR/venv/bin/pip" install psycopg2-binary -q
fi

# =============================================================================
# APLICAR — Migraciones y grupos
# =============================================================================
titulo "Ejecutando migraciones..."
DJANGO_SETTINGS_MODULE=sgai.settings_production \
    "$VENV_PYTHON" "$SCRIPT_DIR/manage.py" makemigrations --noinput
DJANGO_SETTINGS_MODULE=sgai.settings_production \
    "$VENV_PYTHON" "$SCRIPT_DIR/manage.py" migrate --noinput

titulo "Creando grupos de acceso..."
DJANGO_SETTINGS_MODULE=sgai.settings_production \
    "$VENV_PYTHON" "$SCRIPT_DIR/manage.py" crear_grupos

# =============================================================================
# APLICAR — Crear usuarios
# =============================================================================
titulo "Creando usuarios..."

DJANGO_SETTINGS_MODULE=sgai.settings_production \
"$VENV_PYTHON" "$SCRIPT_DIR/manage.py" shell << PYEOF

from django.contrib.auth.models import User, Group

def crear_usuario(username, password, email, first_name, last_name,
                  group_name, is_superuser=False, is_staff=False):
    if not username:
        return
    if User.objects.filter(username=username).exists():
        u = User.objects.get(username=username)
        u.set_password(password)
        u.email = email
        u.first_name = first_name
        u.last_name = last_name
        u.is_superuser = is_superuser
        u.is_staff = is_staff
        u.save()
        print(f"  [ACTUALIZADO] {username}  →  {group_name}")
    else:
        u = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
        u.is_superuser = is_superuser
        u.is_staff = is_staff
        u.save()
        print(f"  [CREADO]      {username}  →  {group_name}")

    if group_name:
        try:
            grupo = Group.objects.get(name=group_name)
            u.groups.set([grupo])
        except Group.DoesNotExist:
            print(f"  [!] Grupo '{group_name}' no encontrado.")

crear_usuario(
    username="${ADMIN_USERNAME}",
    password="${ADMIN_PASS}",
    email="${ADMIN_EMAIL}",
    first_name="${ADMIN_FIRST}",
    last_name="${ADMIN_LAST}",
    group_name="Administrador",
    is_superuser=True,
    is_staff=True,
)

crear_usuario(
    username="${INF_USERNAME}",
    password="${INF_PASS}",
    email="${INF_EMAIL}",
    first_name="${INF_FIRST}",
    last_name="${INF_LAST}",
    group_name="Activos Informáticos",
)

crear_usuario(
    username="${MED_USERNAME}",
    password="${MED_PASS}",
    email="${MED_EMAIL}",
    first_name="${MED_FIRST}",
    last_name="${MED_LAST}",
    group_name="Tecnología Médica",
)

crear_usuario(
    username="${GEN_USERNAME}",
    password="${GEN_PASS}",
    email="${GEN_EMAIL}",
    first_name="${GEN_FIRST}",
    last_name="${GEN_LAST}",
    group_name="Activos Generales",
)

print("")
print("  Usuarios registrados en el sistema:")
print("  " + "─" * 50)
for u in User.objects.all().order_by('username'):
    grupos = ", ".join(u.groups.values_list('name', flat=True)) or \
             ("superusuario" if u.is_superuser else "sin grupo")
    print(f"  {u.username:25} | {u.get_full_name():25} | {grupos}")
PYEOF

# =============================================================================
# Resumen final
# =============================================================================
echo ""
echo "══════════════════════════════════════════════"
ok "Configuración inicial completada."
echo "══════════════════════════════════════════════"
echo ""
echo "  Archivo .env    : $ENV_FILE"
echo "  Settings prod.  : $SETTINGS_PROD"
echo ""
warn "Guarde las contraseñas en un lugar seguro."
warn "No comparta ni versione el archivo .env"
echo ""
