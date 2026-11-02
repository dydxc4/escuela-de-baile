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

## Instalación manual de EDB

### Requerimientos de sistema

- Python 3.14
- MySQL 8.0.46.0
- Node.js 24.21.0 (LTS)
- GTK+ for Windows Runtime Environment Installer 3.24.31

### Instalación de MySQL

Es posible que al instalar MySQL Server aparezca un aviso que indique que se requiere Visual Studio 2019 x64 Redistribute. En cuyo caso, se deberá instalar VS_redist.x64.

Al momento de configurar MySQL por primera vez, se solicita una contraseña para el usuario root, la cual deberá ser edb-root-pwd

Nota: ignorar el aviso de contraseña débil. Todas las configuraciones se dejan tal como están.

Al terminar la instalación será necesario crear una base de datos para el backend, por lo que se deberá abrir desde el menú de inicio MySQL 8.4 Command Line Cliente, ingresar la contraseña anteriormente establecida y en la línea de comando ejecutar "CREATE DATABASE edb;". Solo eso se necesita.

### Instalación de Node.js

Abrir una terminal de PowerShell con privilegios de administrador y ejecutar los siguientes comandos.

1. Habilitar la ejecución de scripts de powershell: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`.
2. Descarga e instala Chocolatey: `powershell -c "irm https://community.chocolatey.org/install.ps1|iex"`.
3. Descarga e instala Node.js (en una nueva pestaña): `choco install nodejs --version="24.21.0"`.
4. Verifica la versión de Node.js (en una nueva pestaña): `node -v` Debería mostrar "v24.21.0".
5. Verifica versión de npm: `npm -v`. Debería mostrar "11.19.0".

### Instalación de GTK+ for Windows

Este componente es requerido para la generación de PDFs. La instalación es simple y directa, sin embargo, se necesita reiniciar después de instalarlo.

### Instalación del sistema

Finalmente, para proceder con la instalación del sistema es necesario contar con una cuenta de correo electrónico y una contraseña de aplicación para habilitar el envío de reportes. Se deberá crear una nueva cuenta (preferentemente de Gmail), generar una contraseña de aplicación y establecerla en el archivo install.ps1 en la sección "$envContent = @".

Posteriormente, se deberá abrir una ventana de la terminal en el mismo directorio donde están los archivos de instalación y, en ella ejecutar lo siguiente:

`.\install.ps1`ls

El script se encargará de crear un entorno virtual dentro de la carpeta `%USERPROFILE%\AppData\Roaming`, instalará las dependencias requeridas, aplicará las migraciones en la base de datos y configurará un servicio para iniciar tanto el backend como el frontend automáticamente.

Para probar que todo funciona correctamente, acceder desde el navegador a las direcciones localhost:3000 y localhost:8000.

Verificar funcionamiento contra XSS.

1. Instalación y Configuración Básica: Instala el paquete vía pip install django-cors-headers y añade 'corsheaders' a INSTALLED_APPS.
2. Orden del Middleware: Es crítico colocar 'corsheaders.middleware.CorsMiddleware'** como **primero** en la lista MIDDLEWARE, antes de CommonMiddlewareoSecurityMiddleware, para que intercepte las peticiones OPTIONS` correctamente.
3. Definición de Orígenes: En settings.py, permite el acceso especificando los orígenes permitidos o habilitando todos (solo para desarrollo):
  - Desarrollo: CORS_ORIGIN_ALLOW_ALL = True
  - Producción: CORS_ALLOWED_ORIGINS = ["http://127.0.0.1:8000"]
4. Verificación de Credenciales: Si usas cookies o autenticación, establece CORS_ALLOW_CREDENTIALS = True, pero nunca combines esto con CORS_ORIGIN_ALLOW_ALL = True, ya que los navegadores bloquearán la petición por seguridad.
