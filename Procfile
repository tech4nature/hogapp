release: cd hog && python manage.py migrate && python manage.py collectstatic --noinput
web: cd hog && gunicorn hog.wsgi --timeout 90
worker: cd hog && python manage.py worker
