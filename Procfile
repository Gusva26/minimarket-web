web: cd backend && gunicorn pos_minimarket.wsgi --bind 0.0.0.0:$PORT --workers 4 --timeout 120
release: cd backend && python manage.py migrate --noinput