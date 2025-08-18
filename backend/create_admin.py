#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@pmcell.com', 'admin123')
    print("Superusuário 'admin' criado com sucesso!")
    print("Username: admin")
    print("Password: admin123")
else:
    print("Superusuário 'admin' já existe!")