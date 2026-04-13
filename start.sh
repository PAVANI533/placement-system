#!/usr/bin/env bash
python manage.py migrate
gunicorn placement_system.wsgi:application