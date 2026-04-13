#!/usr/bin/env bash

echo "Running migrations..."
python manage.py migrate

echo "Starting server..."
gunicorn placement_system.wsgi:application