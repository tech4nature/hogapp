release: cd hog && python manage.py migrate
web: cd hog && gunicorn hog.wsgi --timeout 90
worker: cd hog && python manage.py worker