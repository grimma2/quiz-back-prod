#!/usr/bin/env bash
# exit on error
set -o errexit

python -m ensurepip --default-pip
celery -A quiz worker -l info
python manage.py createsuperuser --email chella05andrey@gmail.com --username anama --noinput