from unicodedata import category
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User, Product, Cart, Order, Wallet
from .serializers import RegisterSerializer, ProductSerializer, CartSerializer, OrderSerializer, WalletSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from decimal import Decimal
from django.db.models import Sum, Count
from django.utils.dateparse import parse_date
from django.utils.timezone import make_aware
from datetime import datetime
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView, RetrieveAPIView

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

class AddProductView(generics.CreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class GetProductsView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = None

class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        product = Product.objects.get(id=product_id)

        cart_item, created = Cart.objects.get_or_create(user=user, product=product)
        if not created:
            cart_item.quantity += int(quantity)
        cart_item.save()

        return Response({'message': 'Product added to cart'}, status=status.HTTP_200_OK)

class GetOrderHistory(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        orders = Order.objects.filter(user=user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

class AddFundsToWallet(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get('amount')
        if amount is None:
            return Response({"error": "Amount is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = Decimal(amount)
            if amount <= 0:
                return Response({"error": "Amount must be a positive number"}, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({"error": "Invalid amount. Must be a valid number."}, status=status.HTTP_400_BAD_REQUEST)

        wallet, created = Wallet.objects.get_or_create(user=request.user)
        wallet.balance += amount
        wallet.save()

        return Response({"message": "Funds added", "current_balance": wallet.balance}, status=status.HTTP_200_OK)

class WalletDetails(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        serializer = WalletSerializer(wallet)
        return Response(serializer.data)

class BuyCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        cart_items = Cart.objects.filter(user=user)
        if not cart_items.exists():
            return Response({"error": "Your cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        total_price = sum(item.product.price * item.quantity for item in cart_items)
        wallet, created = Wallet.objects.get_or_create(user=user)

        if wallet.balance < total_price:
            return Response({"error": "Insufficient balance in wallet"}, status=status.HTTP_400_BAD_REQUEST)

        wallet.balance -= total_price
        wallet.save()

        for item in cart_items:
            product = item.product
            if product.no_of_stocks < item.quantity:
                return Response({"error": f"Not enough stock for {product.name}"}, status=status.HTTP_400_BAD_REQUEST)
            product.no_of_stocks -= item.quantity
            product.save()

            Order.objects.create(
                user=user,
                product=product,
                price=product.price * item.quantity,
                date_of_purchase=request.data.get('date_of_purchase')
            )

        cart_items.delete()

        return Response({
            "message": "Purchase successful",
            "total_price": total_price,
            "remaining_balance": wallet.balance
        }, status=status.HTTP_200_OK)

class SalesReportByDateRange(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')

        if not from_date or not to_date:
            return Response({"error": "Both 'from_date' and 'to_date' are required"}, status=status.HTTP_400_BAD_REQUEST)

        from_date_raw = parse_date(from_date)
        to_date_raw = parse_date(to_date)
        from_date = make_aware(datetime.combine(from_date_raw, datetime.min.time()))
        to_date = make_aware(datetime.combine(from_date_raw, datetime.max.time()))

        sales_data = (
            Order.objects.filter(date_of_purchase__range=[from_date, to_date])
            .values('date_of_purchase__date')
            .annotate(count=Count('id'), total_price_sold=Sum('price'))
            .order_by('date_of_purchase__date')
        )

        return Response(sales_data, status=status.HTTP_200_OK)

class SalesReportByBrand(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')

        if not from_date or not to_date:
            return Response({"error": "Both 'from_date' and 'to_date' are required"}, status=status.HTTP_400_BAD_REQUEST)

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
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class OrderHistoryView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    pagination_class = OrderHistoryPagination

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-date_of_purchase')

class ProductPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class GetAllProductsView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = ProductPagination

class GetProductsByCategoryView(ListAPIView):
    serializer_class = ProductSerializer
    pagination_class = ProductPagination

    def post(self, request, *args, **kwargs):
        category_id = request.data.get('category')
        brand_id = request.data.get('brand', None)

        queryset = Product.objects.filter(category=category_id)
        if brand_id:
            queryset = queryset.filter(brand_id=brand_id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page, many=True).data)
        else:
            serializer = self.serializer_class(queryset, many=True)

        return Response(serializer.data)

class GetProductByIdView(RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'id'
