# Guía de Despliegue – ASSE-GestIT

Esta guía describe el proceso recomendado para preparar, desplegar y operar el sistema **ASSE-GestIT / ASSE-GestACT** en entornos de pruebas, preproducción y producción. Se basa en la arquitectura presentada en `arquitectura_despliegue.drawio` y en los scripts incluidos en este repositorio.

---

## 1. Alcance y objetivos

- Definir los componentes involucrados en la puesta en marcha (frontend, backend, base de datos, servicios externos).
- Establecer requisitos mínimos de infraestructura y dependencias de sistema.
- Proveer pasos reproducibles para despliegues en servidores Linux (Ubuntu/Debian). Se incluyen notas para Windows y contenedores.
- Documentar tareas posteriores al despliegue: verificación, monitoreo, respaldos y actualizaciones.

---

## 2. Arquitectura de referencia

El diagrama `arquitectura_despliegue.drawio` (ver carpeta raíz) describe la separación en zonas:

- **Zona Clientes**: navegadores de usuarios finales (soporte, administrativos).
- **Zona Perimetral / DMZ**: balanceador o proxy inverso (Nginx/Traefik) con terminación TLS, compresión y entrega de estáticos.
- **Zona de Aplicación**: contenedores (o servicios) para frontend estático y backend Django + DRF (Gunicorn como WSGI recomendado), más servicios auxiliares (SMTP, autenticación corporativa, APIs externas).
- **Zona de Datos**: servidor de base de datos (SQLite para pruebas, PostgreSQL/MySQL/Oracle para producción) y almacenamiento de archivos.

Se recomienda exportar el draw.io a PNG/SVG para documentación ejecutiva. Desde app.diagrams.net: `Archivo → Exportar como → PNG`.

---

## 3. Ambientes sugeridos

| Ambiente       | Propósito                                   | Características clave |
|----------------|----------------------------------------------|------------------------|
| Desarrollo     | Trabajo local de desarrolladores             | SQLite, DEBUG=True, scripts `setup.sh`/`run_server.sh` |
| QA / Staging   | Validación previa al paso a producción       | Base de datos aislada, datos sanitizados, DEBUG=False |
| Producción     | Operación con usuarios finales               | HA proxy, Gunicorn + Nginx, base de datos corporativa |

---

## 4. Requisitos de infraestructura

### 4.1 Servidor Linux (Ubuntu 22.04+ recomendado)

- 2 vCPU / 4 GB RAM (mínimo) para despliegue completo backend + frontend estático.
- 20 GB de disco para código, dependencias y archivos media (ajustar según volumen de reportes generados).
- Acceso a Internet para instalación de dependencias y certificados TLS.
- Firewall con puertos 22/80/443 (y 8000/5173 solo en ambientes de desarrollo interno).

### 4.2 Paquetes básicos

```bash
sudo apt update && sudo apt install -y \
    python3 python3-venv python3-pip git nginx \
    build-essential libpq-dev pkg-config
```

Para bases de datos externas instalar el cliente correspondiente (`postgresql-client`, `mysql-client`, etc.).

---

## 5. Preparación del servidor

1. **Crear usuario de servicio (opcional)**

    ```bash
    sudo adduser --system --group --home /opt/asse-gestit asse
    sudo mkdir -p /opt/asse-gestit/app
    sudo chown -R asse:asse /opt/asse-gestit
    ```

2. **Clonar repositorio**

    ```bash
    cd /opt/asse-gestit/app
    git clone <URL-del-repositorio> .
    ```

3. **Crear entorno virtual**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    ```

> Para entornos Windows, consulte `SETUP_INSTRUCTIONS.md` y utilice `setup.bat`.

---

## 6. Configuración de la aplicación

### 6.1 Variables de entorno

Se recomienda centralizar la configuración sensible (SECRET_KEY, credenciales DB, flags de debug) en un archivo `.env` o en el servicio de secrets corporativo.

| Variable               | Descripción                                              | Ejemplo |
|-----------------------|----------------------------------------------------------|---------|
| `DJANGO_SECRET_KEY`   | Llave secreta única por ambiente                         | `DJANGO_SECRET_KEY='cadena-segura'` |
| `DJANGO_DEBUG`        | `True`/`False`                                           | `False` |
| `DJANGO_ALLOWED_HOSTS`| Lista separada por comas de dominios/IPS                 | `inventario.asse.gub.uy` |
| `DJANGO_DB_ENGINE`    | Backend de BD (`django.db.backends.postgresql`)          | `django.db.backends.postgresql` |
| `DJANGO_DB_NAME`      | Nombre de la base                                        | `gestit` |
| `DJANGO_DB_USER`      | Usuario de base de datos                                 | `gestit_app` |
| `DJANGO_DB_PASSWORD`  | Contraseña de base de datos                              | `********` |
| `DJANGO_DB_HOST`      | Host/servicio DB                                         | `10.20.0.15` |
| `DJANGO_DB_PORT`      | Puerto DB                                                | `5432` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Dominios permitidos para CSRF                    | `https://inventario.asse.gub.uy` |

### 6.2 Lectura de variables en `sgai/settings.py`

Antes de ir a producción, adapte el archivo para usar `os.environ`. Ejemplo (añadir al inicio del archivo):

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'change-me')
DEBUG = os.getenv('DJANGO_DEBUG', 'False').lower() == 'true'
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '').split(',') if not DEBUG else []

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DJANGO_DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.getenv('DJANGO_DB_NAME', BASE_DIR / 'db.sqlite3'),
        'USER': os.getenv('DJANGO_DB_USER', ''),
        'PASSWORD': os.getenv('DJANGO_DB_PASSWORD', ''),
        'HOST': os.getenv('DJANGO_DB_HOST', ''),
        'PORT': os.getenv('DJANGO_DB_PORT', ''),
    }
}

CSRF_TRUSTED_ORIGINS = os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS', '').split(',')
```

Asegúrese de definir `STATIC_ROOT = BASE_DIR / 'staticfiles'` para la compilación de recursos en producción.

### 6.3 Paquetes adicionales

Para ejecución con Gunicorn:

```bash
pip install gunicorn
```

Añada el paquete al `requirements.txt` tras validar.

---

## 7. Base de datos

### 7.1 SQLite (desarrollo)

El archivo `db.sqlite3` se crea automáticamente. No se recomienda para producción.

### 7.2 PostgreSQL / MySQL / Oracle

Se incluyen scripts base en la raíz (`init_postgresql.sql`, `init_mysql.sql`, `init_oracle.sql`) con la estructura mínima. Pasos generales:

1. Crear base de datos y usuario con privilegios limitados.
2. Configurar variables de entorno `DJANGO_DB_*` según el motor.
3. Ejecutar migraciones desde el servidor de aplicación: `source venv/bin/activate && python manage.py migrate`.

### 7.3 Datos iniciales

- `crear_bd.py`, `crear_bd_automatico.py` y `crear_datos_maestros.py` contienen rutinas de carga. Ejecute bajo supervisión si necesita catálogos base.
- `dump_backup.json` puede utilizarse con `python manage.py loaddata dump_backup.json`.

---

## 8. Gestión de estáticos y archivos media

1. Defina `STATIC_ROOT` en `settings.py` (ver sección 6.2).
2. Ejecute: `python manage.py collectstatic`.
3. Configure el proxy (Nginx) para servir `/static/` desde esa ruta.
4. El directorio `media/` debe alojarse en almacenamiento persistente y con permisos de escritura para el proceso de Gunicorn. Considere montar un volumen compartido o servicio S3 compatible.

---

## 9. Servicio de aplicación (Gunicorn)

Crear archivo `/etc/systemd/system/gestit.service`:

```ini
[Unit]
Description=ASSE-GestIT Gunicorn
After=network.target

[Service]
User=asse
Group=asse
WorkingDirectory=/opt/asse-gestit/app
Environment="PATH=/opt/asse-gestit/app/venv/bin"
EnvironmentFile=/opt/asse-gestit/app/.env
ExecStart=/opt/asse-gestit/app/venv/bin/gunicorn \
  --workers 3 --bind unix:/opt/asse-gestit/app/run/gunicorn.sock \
  sgai.wsgi:application

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Luego:

```bash
sudo mkdir -p /opt/asse-gestit/app/run
sudo chown asse:asse /opt/asse-gestit/app/run
sudo systemctl daemon-reload
sudo systemctl enable --now gestit.service
```

---

## 10. Proxy reverso y TLS (Nginx)

Archivo `/etc/nginx/sites-available/gestit.conf`:

```nginx
server {
    listen 80;
    server_name inventario.asse.gub.uy;

    location /.well-known/acme-challenge/ {
        root /var/www/letsencrypt;
    }

    location /static/ {
        alias /opt/asse-gestit/app/staticfiles/;
        add_header Cache-Control "public, max-age=86400";
    }

    location /media/ {
        alias /opt/asse-gestit/app/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/opt/asse-gestit/app/run/gunicorn.sock;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Activar sitio:

```bash
sudo ln -s /etc/nginx/sites-available/gestit.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

Para certificados TLS utilizar Certbot/Let’s Encrypt (`sudo certbot --nginx`).

---

## 11. Scripts provistos

| Script               | Uso principal |
|----------------------|---------------|
| `setup.sh`           | Inicializa entorno virtual, instala dependencias y aplica migraciones (Linux/macOS). |
| `setup.bat`          | Equivalente para Windows. |
| `run_server.sh`      | Arranca el servidor de desarrollo asegurando migraciones. |
| `crear_bd*.py`       | Poblado inicial de catálogos y datos maestros. |
| `crear_datos_maestros.py` | Crea registros base para catálogos jerárquicos. |
| `verificar_lugares.py` | Herramienta de comprobación de jerarquía de lugares. |

En producción utilice `systemd` + `gunicorn` en lugar de `run_server.sh`.

---

## 12. Verificación post despliegue

1. Revisar logs (`journalctl -u gestit.service -f`).
2. Ejecutar pruebas automatizadas antes de liberar: `python manage.py test inventario.tests`.
3. Pruebas manuales:
   - Iniciar sesión en `/seteo/login/`.
   - Crear/editar un equipo.
   - Generar una orden de servicio y confirmar descarga del PDF.
   - Revisar dashboard de Tecnología Médica verificando filtros.

---

## 13. Operación y mantenimiento

- **Backups**: programar `python manage.py dumpdata > backups/$(date +%F).json` y respaldo paralelo de la base (pg_dump/mysqldump).
- **Logs**: activar rotación (`logrotate`) para Nginx y Gunicorn.
- **Actualizaciones**: `git pull`, `pip install -r requirements.txt`, `python manage.py migrate`, `collectstatic`, reiniciar servicio.
- **Monitoreo**: agregar sondas HTTP en el proxy (health-check a `/` o `/api/health/` si se expone) y alertas sobre errores 5xx.
- **Seguridad**: mantener `DEBUG=False`, restringir `ALLOWED_HOSTS`, revisar CORS si se expone a dominios adicionales.

---

## 14. Notes sobre contenedores (opcional)

La arquitectura admite despliegue en contenedores:

1. Crear imagen backend (Python base) instalando `requirements.txt`, ejecutando `collectstatic` y exponiendo Gunicorn.
2. Servir frontend como archivos estáticos desde Nginx o CDN.
3. Orquestar con Docker Compose o Kubernetes, replicando la separación de zonas (proxy → backend → base de datos).
4. Asegurar volumen persistente para `/opt/asse-gestit/app/media/`.

(Actualmente el repositorio no incluye Dockerfile; generarlo en caso de adoptar esta estrategia.)

---

## 15. Solución de problemas comunes

| Problema | Acción sugerida |
|----------|-----------------|
| `ModuleNotFoundError: django` | Verifique entorno virtual activo y reinstale dependencias (`pip install -r requirements.txt`). |
| Error CSRF en login | Añada dominio a `DJANGO_CSRF_TRUSTED_ORIGINS` y `ALLOWED_HOSTS`. |
| Archivos estáticos 404 | Asegure `collectstatic`, permisos sobre `STATIC_ROOT` y regla Nginx `/static/`. |
| PDFs no generan | Verifique instalación de ReportLab (incluido en `requirements.txt`) y permisos de escritura en `media/`. |
| Descarga de Excel falla | Instale `openpyxl` (ya listado) y compruebe memoria libre en el servidor. |

---

## 16. Referencias internas

- `README.md`: guía rápida de instalación.
- `SETUP_INSTRUCTIONS.md`: pasos detallados de configuración inicial.
- `DESPLIEGUE.md` (este documento) debe mantenerse actualizado con cada cambio de infraestructura.
- `arquitectura_despliegue.drawio`: fuente del diagrama oficial de despliegue.

> Última actualización: 13/11/2025.
