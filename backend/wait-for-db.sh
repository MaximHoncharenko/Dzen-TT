#!/bin/sh

echo "Очікування бази даних..."

until nc -z db 5432; do
  sleep 1
done

echo "База даних готова — запускаємо Django"
exec "$@"
