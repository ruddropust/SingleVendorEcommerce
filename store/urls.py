from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.home, name='home'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    
    # Shopping Cart
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Checkout & Stripe Integration
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/success/', views.payment_success, name='payment_success'),
    path('checkout/cancel/', views.payment_cancel, name='payment_cancel'),
    
    # Order History & Tracking
    path('orders/', views.order_history, name='order_history'),
    path('orders/<int:order_id>/track/', views.order_track, name='order_track'),
]
