#!/usr/bin/env bash
set -e

echo "Esperando base de datos en ${DB_HOST}:${DB_PORT}..."
until nc -z "${DB_HOST:-db}" "${DB_PORT:-3306}"; do
  sleep 1
done

python manage.py migrate --noinput || true
python manage.py collectstatic --noinput || true

# Crear superusuario automáticamente (solo si se definen variables en el entorno)
if [[ -n "${DJANGO_SUPERUSER_USERNAME:-}" && -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]]; then
  echo "Asegurando superusuario '${DJANGO_SUPERUSER_USERNAME}'..."
  python manage.py shell -c "
import os
from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL') or 'admin@example.com'
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

u, created = User.objects.get_or_create(username=username, defaults={'email': email})
u.email = email
u.is_staff = True
u.is_superuser = True
u.set_password(password)
u.save()
print(('created' if created else 'updated') + ' superuser ' + username)
" || true
else
  echo "DJANGO_SUPERUSER_USERNAME/PASSWORD no definidos; omitiendo creación de superusuario."
fi

# Servidor estable de producción (sin autoreload)
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
