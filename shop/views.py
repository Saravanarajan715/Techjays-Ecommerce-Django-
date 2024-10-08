""" 
Views module for the shop app.

This module contains the API views for user registration, managing products,
carts, orders, and wallets.
"""

from decimal import Decimal
from datetime import datetime
from django.utils.dateparse import parse_date
from django.utils.timezone import make_aware
from django.db.models import Sum, Count
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView, RetrieveAPIView
from .models import User, Product, Cart, Order, Wallet
from .serializers import (
    RegisterSerializer, ProductSerializer, OrderSerializer, WalletSerializer
)

class RegisterView(generics.CreateAPIView):
    """API view to handle user registration."""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


class AddProductView(generics.CreateAPIView):
    """API view to add a new product to the store."""
    permission_classes = [IsAdminUser]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class GetProductsView(generics.ListAPIView):
    """API view to get the list of products."""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = None


class AddToCartView(APIView):
    """API view to add products to the user's cart."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Add a product to the user's cart."""
        user = request.user
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        cart_item, _ = Cart.objects.get_or_create(user=user, product=product)
        cart_item.quantity += int(quantity)
        cart_item.save()

        return Response({'message': 'Product added to cart'}, status=status.HTTP_200_OK)


class GetOrderHistory(APIView):
    """API view to get the user's order history."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve the user's order history."""
        user = request.user
        orders = Order.objects.filter(user=user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class AddFundsToWallet(APIView):
    """API view to add funds to the user's wallet."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Add funds to the user's wallet."""
        amount = request.data.get('amount')
        if amount is None:
            return Response({"error": "Amount is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = Decimal(amount)
            if amount <= 0:
                return Response({"error": "Amount must be a positive number"},
                                 status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({"error": "Invalid amount. Must be a valid number."},
                             status=status.HTTP_400_BAD_REQUEST)

        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        wallet.balance += amount
        wallet.save()

        return Response({"message": "Funds added", "current_balance": wallet.balance},
                         status=status.HTTP_200_OK)


class WalletDetails(APIView):
    """API view to get the wallet details."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve the wallet details of the user."""
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        serializer = WalletSerializer(wallet)
        return Response(serializer.data)


class BuyCartView(APIView):
    """API view to handle the cart purchase process."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Purchase items in the user's cart."""
        user = request.user
        cart_items = Cart.objects.filter(user=user)
        if not cart_items.exists():
            return Response({"error": "Your cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        total_price = sum(item.product.price * item.quantity for item in cart_items)
        wallet, _ = Wallet.objects.get_or_create(user=user)

        if wallet.balance < total_price:
            return Response({"error": "Insufficient balance in wallet"},
                             status=status.HTTP_400_BAD_REQUEST)

        wallet.balance -= total_price
        wallet.save()

        for item in cart_items:
            product = item.product
            if product.no_of_stocks < item.quantity:
                return Response(
                    {"error": f"Not enough stock for {product.name}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            product.no_of_stocks -= item.quantity
            product.save()

            Order.objects.create(
                user=user,
                product=product,
                price=product.price * item.quantity,
                date_of_purchase=request.data.get('date_of_purchase', datetime.now())
            )

        cart_items.delete()

        return Response({
            "message": "Purchase successful",
            "total_price": total_price,
            "remaining_balance": wallet.balance
        }, status=status.HTTP_200_OK)


class SalesReportByDateRange(APIView):
    """API view to generate a sales report within a date range."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        """Generate a sales report for the specified date range."""
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')

        if not from_date or not to_date:
            return Response(
                {"error": "Both 'from_date' and 'to_date' are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        from_date_raw = parse_date(from_date)
        to_date_raw = parse_date(to_date)
        from_date = make_aware(datetime.combine(from_date_raw, datetime.min.time()))
        to_date = make_aware(datetime.combine(to_date_raw, datetime.max.time()))

        sales_data = (
            Order.objects.filter(date_of_purchase__range=[from_date, to_date])
            .values('date_of_purchase__date')
            .annotate(count=Count('id'), total_price_sold=Sum('price'))
            .order_by('date_of_purchase__date')
        )

        return Response(sales_data, status=status.HTTP_200_OK)


class SalesReportByBrand(APIView):
    """API view to generate a sales report by brand within a date range."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        """Generate a sales report by brand for the specified date range."""
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')

        if not from_date or not to_date:
            return Response(
                {"error": "Both 'from_date' and 'to_date' are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        from_date_raw = parse_date(from_date)
        to_date_raw = parse_date(to_date)
        from_date = make_aware(datetime.combine(from_date_raw, datetime.min.time()))
        to_date = make_aware(datetime.combine(to_date_raw, datetime.max.time()))

        sales_data = (
            Order.objects.filter(date_of_purchase__range=[from_date, to_date])
            .values('product__brand')
            .annotate(count=Count('id'), total_price_sold=Sum('price'))
            .order_by('product__brand')
        )

        return Response(sales_data, status=status.HTTP_200_OK)


class OrderHistoryPagination(PageNumberPagination):
    """Custom pagination for order history."""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class OrderHistoryView(ListAPIView):
    """API view to get the paginated order history of a user."""
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    pagination_class = OrderHistoryPagination

    def get_queryset(self):
        """Retrieve the order history for the authenticated user."""
        return Order.objects.filter(user=self.request.user).order_by('-date_of_purchase')


class ProductPagination(PageNumberPagination):
    """Custom pagination for products."""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class GetAllProductsView(ListAPIView):
    """API view to get the list of all products with pagination."""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = ProductPagination


class GetProductsByCategoryView(ListAPIView):
    """API view to get products filtered by category and brand."""
    serializer_class = ProductSerializer
    pagination_class = ProductPagination

    def post(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        """Retrieve products by category and optional brand."""
        category_id = request.data.get('category')
        brand_id = request.data.get('brand', None)

        queryset = Product.objects.filter(category=category_id)
        if brand_id:
            queryset = queryset.filter(brand=brand_id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page, many=True).data)
        else:
            serializer = self.serializer_class(queryset, many=True)

        return Response(serializer.data)


class GetProductByIdView(RetrieveAPIView):
    """API view to retrieve product details by ID."""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'id'
