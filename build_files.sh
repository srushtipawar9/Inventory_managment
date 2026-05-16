#!/bin/bash
set -e
echo "Building project packages..."
pip3 install -r requirements.txt --break-system-packages

echo "Running database migrations..."
python3 manage.py migrate --noinput

echo "Collecting static files..."
python3 manage.py collectstatic --noinput --clear
