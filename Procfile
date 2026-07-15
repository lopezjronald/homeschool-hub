release: python manage.py migrate
web: gunicorn homeschool_hub.wsgi --workers 2 --threads 4 --timeout 30 --max-requests 500 --max-requests-jitter 50 --log-file -
