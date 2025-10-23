web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --threads 2
release: python manage.py migrate --no-input && python manage.py setup_superuser && python manage.py create_test_data
