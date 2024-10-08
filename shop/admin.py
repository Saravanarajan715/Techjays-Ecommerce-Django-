"""
Admin module for the shop application. This module registers models with
the Django admin site to enable their management via the admin interface.
"""
from django.contrib import admin
from .models import User, Product, Order, Cart, Wallet
admin.site.register(User)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Cart)
admin.site.register(Wallet)
