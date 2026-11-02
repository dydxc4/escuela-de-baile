# install.ps1
$ErrorActionPreference = "Stop"

# 1. Definición de Rutas
$scriptPath = $PSScriptRoot
$targetDir = "$env:APPDATA\EDB_v1"
$backendZip = "$scriptPath\backend-main.zip"
$frontendZip = "$scriptPath\frontend-main.zip"

Write-Host "Iniciando comprobación de requisitos del sistema..." -ForegroundColor Cyan

# 2. Comprobación de Requisitos (Python, Node.js, MySQL)
try {
    $pythonVersion = & python --version 2>&1
    Write-Host "✅ Python detectado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Python no está instalado o no está en el PATH." -ForegroundColor Red
    exit
}

try {
    $nodeVersion = & node -v 2>&1
    Write-Host "✅ Node.js detectado: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Node.js no está instalado o no está en el PATH." -ForegroundColor Red
    exit
}

$mysqlService = Get-Service -Name "MySQL84" -ErrorAction SilentlyContinue
if ($mysqlService) {
    Write-Host "✅ Servicio MySQL detectado: $($mysqlService.Name) ($($mysqlService.Status))" -ForegroundColor Green
    if ($mysqlService.Status -ne "Running") {
        Write-Host "Iniciando MySQL..." -ForegroundColor Yellow
        Start-Service -Name $mysqlService.Name
    }
} else {
    Write-Host "⚠️️ Advertencia: No se detectó un servicio de Windows nativo llamado 'MySQL*'. Asegúrate de que el DBMS esté corriendo." -ForegroundColor Yellow
}

# 3. Creación de Directorio y Extracción
Write-Host "`nPreparando el directorio de la aplicación en $targetDir..." -ForegroundColor Cyan
if (!(Test-Path $targetDir)) {
    New-Item -ItemType Directory -Force -Path $targetDir | Out-Null
}

Write-Host "Extrayendo backend y frontend..." -ForegroundColor Yellow
if (Test-Path $backendZip) {
  Expand-Archive -Path $backendZip -DestinationPath "$targetDir" -Force
  Rename-Item -Path "$targetDir\escuela-de-baile-main" -NewName "backend"
}
if (Test-Path $frontendZip) {
  Expand-Archive -Path $frontendZip -DestinationPath "$targetDir" -Force
  Rename-Item -Path "$targetDir\escuela-de-baile-front-main" -NewName "frontend"
}

# 4. Configuración del Backend (Entorno Virtual y Dependencias)
Write-Host "`nConfigurando el Backend (Django)..." -ForegroundColor Cyan
Set-Location "$targetDir\backend"

Write-Host "Creando entorno virtual..." -ForegroundColor Yellow
& python -m venv venv

Write-Host "Instalando dependencias de Python y Waitress..." -ForegroundColor Yellow
& ".\venv\Scripts\python.exe" -m pip install --upgrade pip | Out-Null
& ".\venv\Scripts\pip.exe" install -r requirements.txt
& ".\venv\Scripts\pip.exe" install waitress django-environ

Write-Host "Generando archivo .env..." -ForegroundColor Yellow
$envContent = @"
DB_HOST=127.0.0.1
DB_NAME=edb
DB_USER=root
DB_PASS=edb-root-pwd
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
SECRET_KEY=aSJiiGz_gjaKA8&d
DEBUG=False
"@
$envContent | Out-File -FilePath "$targetDir\backend\.env" -Encoding utf8

Write-Host "Aplicando migraciones a la base de datos..." -ForegroundColor Yellow
Set-Location "$targetDir\backend\edb"
& "..\venv\Scripts\python.exe" manage.py migrate

# 5. Configuración del Frontend (Next.js)
Write-Host "`nConfigurando el Frontend (Next.js)..." -ForegroundColor Cyan
Set-Location "$targetDir\frontend"

Write-Host "Instalando dependencias de Node..." -ForegroundColor Yellow
& npm install

Write-Host "Construyendo la aplicación para producción..." -ForegroundColor Yellow
& npm run build

# 6. Orquestación de Servicios con PM2
Write-Host "`nConfigurando servicios de arranque automático con PM2..." -ForegroundColor Cyan
Set-Location $targetDir

if (!(Get-Command pm2 -ErrorAction SilentlyContinue)) {
    Write-Host "Instalando PM2 globalmente..." -ForegroundColor Yellow
    & npm install -g pm2 pm2-windows-startup
}

Write-Host "Creando ecosystem.config.js..." -ForegroundColor Yellow
$ecosystemContent = @"
module.exports = {
  apps: [
    {
      name: "backend-api",
      cwd: "./backend/edb",
      script: "../venv/Scripts/waitress-serve.exe",
      args: "--listen=127.0.0.1:8000 edb.wsgi:application",
    },
    {
      name: "frontend-web",
      cwd: "./frontend",
      script: "serve",
      env: {
        PM2_SERVE_PATH: "./dist",
        PM2_SERVE_PORT: 3000,
        PM2_SERVE_SPA: "true",
        PM2_SERVE_HOMEPAGE: "/index.html"
      }
    }
  ]
};
"@
$ecosystemContent | Out-File -FilePath "$targetDir\ecosystem.config.js" -Encoding utf8

Write-Host "Iniciando y guardando procesos en PM2..." -ForegroundColor Yellow
& pm2 start ecosystem.config.js
& pm2 save
& pm2-startup

Write-Host "`n✅ ¡Despliegue completado con éxito! La plataforma está corriendo en segundo plano." -ForegroundColor Green
