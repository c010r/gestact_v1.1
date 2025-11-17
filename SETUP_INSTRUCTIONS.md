# ASSE-GestACT - Instrucciones de Configuración

## 📋 Requisitos Previos

### Windows
- Python 3.8 o superior
- Git

### Linux/Ubuntu
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv git
```

### macOS
```bash
brew install python3 git
```

## 🚀 Configuración Inicial

### Para Windows
```cmd
# Clonar el repositorio
git clone <url-del-repositorio>
cd ASSE-GestACT

# Ejecutar script de configuración
setup.bat
```

### Para Linux/macOS
```bash
# Clonar el repositorio
git clone <url-del-repositorio>
cd ASSE-GestACT

# Dar permisos de ejecución
chmod +x setup.sh
chmod +x run_server.sh

# Ejecutar script de configuración
./setup.sh
```

## 🖥️ Ejecutar el Servidor

### Windows
```cmd
# Activar entorno virtual
venv\Scripts\activate.bat

# Iniciar servidor
python manage.py runserver
```

### Linux/macOS
```bash
# Opción 1: Script automático
./run_server.sh

# Opción 2: Manual
source venv/bin/activate
python manage.py runserver
```

## 🌐 Acceso a la Aplicación

Una vez iniciado el servidor, accede a:
- **URL Principal**: http://127.0.0.1:8000/
- **Panel de Login**: http://127.0.0.1:8000/seteo/login/

### Credenciales por Defecto
- **Usuario**: `admin`
- **Contraseña**: `admin123`

## 📁 Estructura del Proyecto

```
ASSE-GestACT/
├── setup.bat          # Script de configuración para Windows
├── setup.sh           # Script de configuración para Linux/macOS
├── run_server.sh      # Script para ejecutar servidor (Linux/macOS)
├── requirements.txt   # Dependencias de Python
├── manage.py         # Comando principal de Django
├── db.sqlite3        # Base de datos SQLite (se crea automáticamente)
├── sgai/             # Configuración principal del proyecto (paquete interno)
├── seteo/            # Aplicación de configuración
└── inventario/       # Aplicación de inventario
```

## 🔧 Comandos Útiles

### Crear un superusuario
```bash
python manage.py createsuperuser
```

### Resetear la base de datos
```bash
# Eliminar base de datos
rm db.sqlite3

# Recrear migraciones
python manage.py makemigrations
python manage.py migrate
```

### Instalar nuevas dependencias
```bash
pip install <paquete>
pip freeze > requirements.txt
```

## ❗ Solución de Problemas

### Error: "No module named 'django'"
- Asegúrate de que el entorno virtual esté activado
- Ejecuta: `pip install -r requirements.txt`

### Error: "Permission denied" (Linux/macOS)
- Ejecuta: `chmod +x setup.sh run_server.sh`

### Error de migraciones
- Ejecuta: `python manage.py makemigrations`
- Luego: `python manage.py migrate`

## 📞 Soporte

Si encuentras problemas durante la configuración, verifica:
1. Que Python esté correctamente instalado
2. Que el entorno virtual esté activado
3. Que todas las dependencias estén instaladas
4. Que los permisos de archivos sean correctos (Linux/macOS)