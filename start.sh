#!/usr/bin/env bash
gunicorn placement_system.wsgi:application