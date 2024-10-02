from django.contrib import admin

# Register your models here.

from .models import User, Product, Order, Cart, Wallet


admin.site.register(User)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Cart)
admin.site.register(Wallet)
