"""
URL configuration for the 'shop' app.

This module defines the URL patterns for the views in the application,
such as registering users, managing products, carts, orders, and wallets.
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from .views import (
    AddFundsToWallet, GetProductByIdView, GetProductsByCategoryView, OrderHistoryView, RegisterView,
    AddProductView, GetProductsView, AddToCartView, BuyCartView, GetOrderHistory,
    SalesReportByBrand, SalesReportByDateRange, WalletDetails
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('add-product/', AddProductView.as_view(), name='add_product'),
    path('get-products/', GetProductsView.as_view(), name='get_products'),
    path('add-to-cart/', AddToCartView.as_view(), name='add_to_cart'),
    path('buy-cart/', BuyCartView.as_view(), name='buy_cart'),
    path('get-order-history/', GetOrderHistory.as_view(), name='get_order_history'),
    path('add-wallet/', AddFundsToWallet.as_view(), name='add_wallet'),
    path('wallet/', WalletDetails.as_view(), name='wallet_details'),
    path('sales-report/', SalesReportByDateRange.as_view(), name='sales_report_by_date_range'),
    path('sales-report-by-brand/', SalesReportByBrand.as_view(), name='sales_report_by_brand'),
    path('order-history/', OrderHistoryView.as_view(), name='order_history'),
    path(
        'products-by-category/',
        GetProductsByCategoryView.as_view(),
        name='get_products_by_category'
    ),
    path('product/<int:id>/', GetProductByIdView.as_view(), name='get_product_by_id'),
]
