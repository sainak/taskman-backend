release: python manage.py migrate --noinput
web: gunicorn core.wsgi:application
worker: celery -A core.celery_app worker --loglevel=info
beat: celery -A core.celery_app beat --loglevel=info
