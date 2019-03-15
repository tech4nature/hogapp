Django app for exploring data gathered about hedgehogs


# Installation

## Create environment

1. Set up a python3 virtualenv
2. `pip install pip-tools`
3. `pip-sync`

## Set up admin user

```
cd hog
./manage.py createsuperuser
```

## Generate sample data

    ./manage.py generate_data

## Run server

    ./manage.py runserver

## View api


Visit http://localhost:8000/api/
