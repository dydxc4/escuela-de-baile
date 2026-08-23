# Escuela de Baile

Este es el repositorio para el proyecto de servidor API rest usando Django REST Framework.

## Instalación

**Componentes requeridos:**

- Git
- Python >=3.14 & pip
- Docker Compose

**Pasos:**

1. Clonar este repositorio `git clone https://github.com/dydxc4/edb.git`.
2. Inicializar un nuevo entorno virtual de Python en el directorio raíz del proyecto `python -m venv .venv` (usar `py` en Windows). Habilitar con `source .venv/bin/activate`.
3. Instalar dependencias `pip install -r requirements.txt`.
4. Orquestar servicios con Docker `docker compose up -d`.
6. Aplicar migraciones con `python manage.py migrate` (dentro del directorio `edb`).
7. Crear superusuario con `python manage.py createsuperuser`.
8. Iniciar servidor web con `python manage.py runserver`.

El sitio es accesible a través del localhost en el puerto 8000; Adminer, puerto 8001.

**URLS:**

- Django Admin: `http://localhost:8000/admin/`
- Swagger: `http://localhost:8000/swagger/`
- Redoc: `http://localhost:8000/redoc/`
