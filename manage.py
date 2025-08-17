#!/usr/bin/env python
"""
PMCELL Catálogo - Manage.py Root Wrapper
Este arquivo redireciona para o manage.py do backend
"""
import os
import sys
import subprocess

if __name__ == '__main__':
    # Navegar para a pasta backend e executar o manage.py de lá
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    manage_py = os.path.join(backend_dir, 'manage.py')
    
    if os.path.exists(manage_py):
        os.chdir(backend_dir)
        subprocess.run([sys.executable, 'manage.py'] + sys.argv[1:])
    else:
        print("❌ Backend manage.py not found!")
        sys.exit(1)