

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from rest_framework.generics import ListAPIView
from .models import Product
from .serializers import ProductSerializer
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend 
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from shop.models import Order
from django.utils.timezone import make_aware
from django.utils.dateparse import parse_date
from datetime import datetime

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('customer', 'Customer'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)


class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    no_of_stocks = models.IntegerField()
    brand = models.CharField(max_length=255)


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date_of_purchase = models.DateTimeField(default=timezone.now)



User = get_user_model()

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date_of_purchase = models.DateTimeField(auto_now_add=True)


User = get_user_model()

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.user.username}'s Wallet"
    



from_date_raw = parse_date("2024-09-27") 
to_date_raw = parse_date("2024-09-28")  


from_date = make_aware(datetime.combine(from_date_raw, datetime.min.time()))
to_date = make_aware(datetime.combine(to_date_raw, datetime.max.time()))


orders = Order.objects.filter(date_of_purchase__range=[from_date, to_date])


print(orders)

class ProductPagination(PageNumberPagination):
    page_size = 10  
    page_size_query_param = 'page_size'
    max_page_size = 100


