import uuid
from django.db import models
from django.utils import timezone


class Cake(models.Model):
    CATEGORY_CHOICES = [
        ("Chocolate", "Chocolate Obsession"),
        ("Cheesecake", "Artisan Cheesecakes"),
        ("Fruit", "Fresh Fruit & Berries"),
        ("Exotic", "Exotic & Signature"),
        ("Eggless", "100% Eggless Specials"),
        ("Pastry", "Artisan Pastries"),
    ]

    name = models.CharField(max_length=120)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="Chocolate")
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    original_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    image_url = models.URLField(max_length=500, blank=True)
    badge = models.CharField(max_length=50, blank=True, help_text="e.g. Bestseller, Chef's Special, Trending, New")
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.9)
    reviews_count = models.PositiveIntegerField(default=38)
    is_eggless = models.BooleanField(default=False)
    weight_options = models.CharField(max_length=100, default="0.5 kg, 1 kg, 1.5 kg, 2 kg")
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.name} (₹{self.price})"


class Order(models.Model):
    STATUS_CHOICES = [
        ("Order Placed", "Order Placed"),
        ("Baking in Oven", "Baking in Oven 👩‍🍳"),
        ("Decorating & Packing", "Decorating & Packing 🎁"),
        ("Out for Delivery", "Out for Delivery 🛵"),
        ("Delivered", "Delivered 🎉"),
        ("Cancelled", "Cancelled ❌"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Paid", "Paid (Verified)"),
        ("Failed", "Failed"),
    ]

    order_number = models.CharField(max_length=30, unique=True, editable=False)
    customer_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField()
    delivery_date = models.CharField(max_length=50, blank=True)
    delivery_slot = models.CharField(max_length=50, blank=True)
    cake_message = models.CharField(max_length=150, blank=True, help_text="Custom greeting piped on cake")
    items = models.TextField(help_text="Summary text of items")
    items_json = models.TextField(default="[]", help_text="JSON formatted items for rich tracking")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, default="Razorpay (Online)")
    payment_status = models.CharField(max_length=30, choices=PAYMENT_STATUS_CHOICES, default="Pending")
    razorpay_order_id = models.CharField(max_length=100, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    order_status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="Order Placed")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"SS-{timezone.now().strftime('%y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order_number} - {self.customer_name} (₹{self.total})"
