#!/usr/bin/env bash
set -e

echo "Esperando base de datos en ${DB_HOST}:${DB_PORT}..."
until nc -z "${DB_HOST:-db}" "${DB_PORT:-3306}"; do
  sleep 1
done

python manage.py migrate --noinput || true
python manage.py collectstatic --noinput || true

# Servidor estable de producción (sin autoreload)
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
