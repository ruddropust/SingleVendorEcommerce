from django.contrib import admin
from .models import Category, Product, Order, OrderItem, OrderStatus

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'is_in_stock', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0

class OrderStatusInline(admin.TabularInline):
    model = OrderStatus
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'payment_status', 'order_date')
    list_filter = ('payment_status', 'order_date')
    search_fields = ('user__username', 'stripe_session_id', 'shipping_name')
    inlines = [OrderItemInline, OrderStatusInline]

@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'timestamp')
    list_filter = ('status', 'timestamp')
    search_fields = ('order__id', 'description')
