"""
Health check URL (independiente, sin namespace)
"""
from django.urls import path
from .views import health_check

urlpatterns = [
    path("", health_check, name="health-check"),
]
