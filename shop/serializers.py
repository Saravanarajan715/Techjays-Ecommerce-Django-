"""
This module contains the serializers for the 'shop' application,
which are used to serialize and deserialize data for API endpoints.
"""

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from .models import Product, Cart, Order, Wallet

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model, which includes fields for username, 
    email, first name, last name, and user type.
    
    This serializer is used to create and update user instances 
    while ensuring that the necessary fields are provided.
    """
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'user_type']

    def __init__(self, *args, **kwargs):
        """Initialize UserSerializer with extra validation logic if needed."""
        super().__init__(*args, **kwargs)

class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration, requiring password validation and
    including fields for user details.
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name', 'user_type']

    def create(self, validated_data):
        """
        Custom method to create a new user instance with the given data,
        setting the password correctly.
        """
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            user_type=validated_data['user_type']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class CartSerializer(serializers.ModelSerializer):
    """
    Serializer for the Cart model, which includes fields for the product
    and quantity of items in the user's cart.
    """
    class Meta:
        model = Cart
        fields = ['product', 'quantity']

    def __init__(self, *args, **kwargs):
        """Initialize CartSerializer with extra validation logic if needed."""
        super().__init__(*args, **kwargs)


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Order model, including fields for the product and
    the date of purchase.
    """
    class Meta:
        model = Order
        fields = ['product', 'date_of_purchase']

    def __init__(self, *args, **kwargs):
        """Initialize OrderSerializer with extra validation logic if needed."""
        super().__init__(*args, **kwargs)


class WalletSerializer(serializers.ModelSerializer):
    """
    Serializer for the Wallet model, which includes fields for the user
    and the balance. The balance field is read-only.
    """
    class Meta:
        model = Wallet
        fields = ['user', 'balance']
        read_only_fields = ['user', 'balance']

    def __init__(self, *args, **kwargs):
        """Initialize WalletSerializer with extra validation logic if needed."""
        super().__init__(*args, **kwargs)


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for the Product model, including fields for name, category,
    price, description, number of stocks, and brand.
    """
    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'description', 'no_of_stocks', 'brand']

    def validate_price(self, value):
        """
        Validator to ensure that the product price is a positive value.
        """
        if value <= 0:
            raise serializers.ValidationError("Price must be a positive value.")
        return value

    def validate_no_of_stocks(self, value):
        """
        Validator to ensure that the number of stocks is not a negative value.
        """
        if value < 0:
            raise serializers.ValidationError("Number of stocks cannot be negative.")
        return value

    def __init__(self, *args, **kwargs):
        """Initialize ProductSerializer with extra validation logic if needed."""
        super().__init__(*args, **kwargs)
