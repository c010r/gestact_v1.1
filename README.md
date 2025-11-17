# ASSE-GestACT - Sistema de Gestión de Activos Informáticos

Sistema web para la gestión y control de inventario de activos informáticos, desarrollado con Django REST Framework y React.

## Características

### Módulos Implementados
- **Computadoras**: Gestión completa de equipos de cómputo
- **Impresoras**: Gestión completa de impresoras
- **Dashboard**: Panel de control con estadísticas
- **Referencias**: Gestión de catálogos (fabricantes, modelos, lugares, etc.)

### Funcionalidades
- ✅ CRUD completo para computadoras e impresoras
- ✅ Generación automática de números de inventario
- ✅ Gestión de catálogos dinámicos
- ✅ Cálculo automático de fechas de garantía
- ✅ Interfaz responsive y moderna
- ✅ API REST completa
- ✅ Validaciones de formularios
- ✅ Búsqueda y filtrado
- ✅ Paginación

## Tecnologías

### Backend
- Django 5.1.4
- Django REST Framework
- SQLite (desarrollo)
- Python 3.12

### Frontend
- React 18
- Material-UI (MUI)
- Vite
- Axios
- React Router

## Instalación

### Prerrequisitos
- Python 3.12+
- Node.js 18+
- npm o yarn

### Backend (Django)

1. Clonar el repositorio:
```bash
git clone <repository-url>
cd ASSE-GestACT
```

2. Crear y activar entorno virtual:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Ejecutar migraciones:
```bash
python manage.py migrate
```

5. Poblar base de datos (opcional):
```bash
python populate_db.py
python populate_impresoras.py
```

6. Ejecutar servidor:
```bash
python manage.py runserver
```

### Frontend (React)

1. Navegar al directorio frontend:
```bash
cd frontend
```

2. Instalar dependencias:
```bash
npm install
```

3. Ejecutar servidor de desarrollo:
```bash
npm run dev
```

## Uso

1. Acceder a la aplicación en `http://localhost:5173`
2. El backend estará disponible en `http://localhost:8000`
3. API endpoints disponibles en `http://localhost:8000/api/`

### Endpoints Principales

- `/api/computadoras/` - Gestión de computadoras
- `/api/impresoras/` - Gestión de impresoras
- `/api/fabricantes/` - Catálogo de fabricantes
- `/api/modelos/` - Catálogo de modelos
- `/api/lugares/` - Catálogo de lugares
- `/api/estados/` - Catálogo de estados
- `/api/tipos-impresora/` - Catálogo de tipos de impresora
- `/api/tipos-garantia/` - Catálogo de tipos de garantía
- `/api/proveedores/` - Catálogo de proveedores

## Estructura del Proyecto

```
ASSE-GestACT/
├── backend/
│   ├── inventario/          # App principal
│   ├── sgai/               # Configuración Django (paquete interno)
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/     # Componentes reutilizables
│   │   ├── pages/         # Páginas principales
│   │   └── config/        # Configuración
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Contribución

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## Contacto

Proyecto desarrollado para la gestión de activos informáticos.