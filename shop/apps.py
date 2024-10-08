"""
App configuration for the 'shop' application.

This module defines the configuration for the 'shop' app, including
default auto field settings and app name.
"""

from django.apps import AppConfig


class ShopConfig(AppConfig):
    """
    Configuration class for the 'shop' application. It sets the default 
    auto field and defines the name of the app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shop'
