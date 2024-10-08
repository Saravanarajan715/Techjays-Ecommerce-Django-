"""
Models module for the shop application. This module defines the data models 
used in the application, including user, wallet, product, cart, and order 
models.
"""

from datetime import datetime
from django.utils.dateparse import parse_date
from django.utils.timezone import make_aware
from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework.pagination import PageNumberPagination


class User(AbstractUser):
    """
    Custom User model extending AbstractUser. This model adds user types 
    for different roles in the application.
    """
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('customer', 'Customer'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)


class Wallet(models.Model):
    """
    Model representing a wallet associated with a user. The wallet holds 
    a balance for the user.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        # Ensure that 'user' is properly referenced for the username
        return f"{self.user.username}'s Wallet"


class Product(models.Model):
    """
    Model representing a product available in the shop. This includes 
    information like name, category, price, and stock details.
    """
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    no_of_stocks = models.IntegerField()
    brand = models.CharField(max_length=255)


class Cart(models.Model):
    """
    Model representing a shopping cart for a user. It holds information 
    about the products added to the cart along with their quantities.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)


class Order(models.Model):
    """
    Model representing an order made by a user. It includes details 
    about the user, product, price, and the date of purchase.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date_of_purchase = models.DateTimeField(auto_now_add=True)


class ProductPagination(PageNumberPagination):
    """
    Pagination class for paginating product lists. It defines the 
    page size and maximum page size.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


# Sample usage of parsing dates and filtering orders
def filter_orders():
    """
    Sample function to demonstrate filtering orders based on a date range.
    """
    from_date_raw = parse_date("2024-09-27")
    to_date_raw = parse_date("2024-09-28")

    from_date = make_aware(datetime.combine(from_date_raw, datetime.min.time()))
    to_date = make_aware(datetime.combine(to_date_raw, datetime.max.time()))

    # Fetching orders based on the date range
    orders = Order.objects.filter(date_of_purchase__range=[from_date, to_date])
    return orders


# Uncomment the following line to see the orders when this module is run directly.
#print(filter_orders())
