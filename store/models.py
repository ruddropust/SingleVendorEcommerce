from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
import datetime

class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def is_in_stock(self):
        return self.stock > 0

class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    order_date = models.DateTimeField(auto_now_add=True)
    
    # Shipping details
    shipping_name = models.CharField(max_length=255, blank=True, null=True)
    shipping_address = models.TextField(blank=True, null=True)
    shipping_city = models.CharField(max_length=100, blank=True, null=True)
    shipping_postal_code = models.CharField(max_length=20, blank=True, null=True)
    shipping_country = models.CharField(max_length=100, blank=True, null=True)
    
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order #{self.order.id})"

class OrderStatus(models.Model):
    STATUS_CHOICES = (
        ('Order Placed', 'Order Placed'),
        ('Processing', 'Processing'),
        ('Payment', 'Payment'),
        ('Confirmed', 'Confirmed'),
        ('Packing', 'Packing'),
        ('Packed', 'Packed'),
        ('Delivering', 'Delivering'),
        ('Delivered', 'Delivered'),
    )

    DEFAULT_DESCRIPTIONS = {
        'Order Placed': 'Your order has been registered in our system and is awaiting processing.',
        'Processing': 'We have received your order; our team is checking details and preparing inventory.',
        'Payment': 'Payment has been successfully verified via Stripe.',
        'Confirmed': 'Your order has been confirmed and is ready for packaging.',
        'Packing': 'We are gathering and packing your items in our warehouse.',
        'Packed': 'Your parcel is packed and ready for courier pickup.',
        'Delivering': 'Your package is on the way. Our delivery partner will contact you shortly.',
        'Delivered': 'Your package has been successfully delivered. Thank you for shopping with us!',
    }

    order = models.ForeignKey(Order, related_name='statuses', on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    timestamp = models.DateTimeField(default=timezone.now)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Order Status'
        verbose_name_plural = 'Order Statuses'
        ordering = ['timestamp']

    def save(self, *args, **kwargs):
        if not self.description:
            self.description = self.DEFAULT_DESCRIPTIONS.get(self.status, '')
            
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # Sequence order of steps
            steps_order = [
                'Order Placed',
                'Processing',
                'Payment',
                'Confirmed',
                'Packing',
                'Packed',
                'Delivering',
                'Delivered'
            ]
            
            if self.status in steps_order:
                target_idx = steps_order.index(self.status)
                existing_statuses = set(OrderStatus.objects.filter(order=self.order).values_list('status', flat=True))
                
                # Sequentially create missing prior stages
                for i in range(target_idx):
                    prior_status = steps_order[i]
                    if prior_status not in existing_statuses:
                        # Set timestamp slightly earlier than current status to maintain correct chronological order
                        offset_seconds = (target_idx - i) * 2
                        prior_time = self.timestamp - datetime.timedelta(seconds=offset_seconds)
                        
                        OrderStatus.objects.create(
                            order=self.order,
                            status=prior_status,
                            timestamp=prior_time
                        )
                        existing_statuses.add(prior_status)

    def __str__(self):
        return f"Order #{self.order.id} - {self.status}"
