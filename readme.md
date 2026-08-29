# Escuela de Baile

Este es el repositorio para el proyecto de servidor API rest usando Django REST Framework.

## Instalación

**Componentes requeridos:**

- Git
- Python >=3.14 & pip
- Docker Compose

**Pasos para probar el servidor:**

1. Clonar este repositorio `git clone https://github.com/dydxc4/escuela-de-baile.git`.
2. Inicializar un nuevo entorno virtual de Python en el directorio raíz del proyecto `python -m venv .venv` (usar `py` en Windows). Habilitar con `source .venv/bin/activate` o `.venv\Scripts\Activate.bat` en Windows.
3. Instalar dependencias `pip install -r requirements.txt`.
4. Orquestar servicios con Docker `docker compose up -d`.
6. Aplicar migraciones con `python manage.py migrate` (dentro del directorio `edb`).
7. Crear superusuario con `python manage.py createsuperuser`.
8. Iniciar servidor web con `python manage.py runserver`.

El sitio es accesible a través del localhost en el puerto 8000; Adminer, puerto 8001.

**Despliegue:**

1. Clonar este repositorio.
2. Ejecutar `docker compose up --build -d` para crear una imagen del servidor y orquestarlo.
3. Ejecutat `docker compose ps -a` para verificar que los contenedores se encuentren en ejecución.

El servidor puede iniciarse y detenerse usando los comandos `docker compose start` y `docker compose stop`. Las migraciones se aplican automaticamente a crear una nueva imagen.

Para habilitar el acceso externo al servidor, cambiar la dirección IP enlazada al contenedor edb-backend por `0.0.0.0` en el archivo `docker-compose.yml`.

**URLS:**

- Django Admin: `http://localhost:8000/admin/`
- Swagger: `http://localhost:8000/swagger/`
- Redoc: `http://localhost:8000/redoc/`
