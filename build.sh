#!/usr/bin/env bash
# exit on error
set -o errexit

/opt/render/project/src/.venv/bin/python -m pip install --upgrade pip


python -m ensurepip --default-pip
pip install -r requirements.txt
#python manage.py makemigrations
#python manage.py migrate
#python manage.py createsuperuser --username anama --email chella05andrey@gmail.com --noinput
celery -A quiz worker -l info