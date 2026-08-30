#!/bin/sh
set -e

echo "Aplicando migraciones de la base de datos..."
python manage.py migrate

echo "Iniciando el servidor de aplicaciones..."
exec "$@"
