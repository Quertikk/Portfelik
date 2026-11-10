"""Punkt wejścia WSGI na serwerze (np. PythonAnywhere). SECRET_KEY ustawia się w zmiennych środowiskowych."""
from app import app as application  # noqa: F401
