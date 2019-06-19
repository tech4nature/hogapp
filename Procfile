release: cd hog && python manage.py migrate
web: cd hog && gunicorn hog.wsgi
worker: cd hog && python manage.py worker