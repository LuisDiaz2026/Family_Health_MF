#!/usr/bin/env python
"""
Family Health MF - Entry Point (manage.py)
Trabajo de Grado - Universidad Antonio Nariño
Autor: Luis Fermín Díaz Choles
"""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django no está disponible. Verifica que el entorno virtual esté activado "
            "y las dependencias instaladas (pip install -r requirements.txt)."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
