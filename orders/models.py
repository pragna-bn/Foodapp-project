from django.db import models, transaction
from django.contrib.auth.models import User
from main.models import FoodItem


class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PREPARING', 'Preparing'),
        ('OUT', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    # Customer details for delivery
    customer_name = models.CharField(max_length=200, blank=True, null=True)
    customer_phone = models.CharField(max_length=15, blank=True, null=True)
    customer_address = models.TextField(blank=True, null=True)

    # Sequential order number (fixed)
    order_number = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.order_number or self.id} - {self.user.username} ({self.status})"

    def save(self, *args, **kwargs):
        """
        Assign perfect sequential order numbers and recalculate total.
        No gaps, no duplicates, no old continuation.
        """
        # Assign order_number safely
        if not self.order_number:
            with transaction.atomic():  # Prevent race conditions
                last_number = (
                    Order.objects.select_for_update()
                    .order_by('-order_number')
                    .values_list('order_number', flat=True)
                    .first()
                )
                self.order_number = 1 if last_number is None else last_number + 1

        super().save(*args, **kwargs)

        # Calculate total price based on items
        new_total = sum(item.subtotal for item in self.items.all())

        if self.total_price != new_total:
            self.total_price = new_total
            super().save(update_fields=['total_price'])

    @property
    def can_cancel(self):
        return self.status not in ['DELIVERED', 'CANCELLED']


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    food = models.ForeignKey(
        FoodItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_items'
    )
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ['order', 'food']

    def __str__(self):
        if self.food:
            return f"{self.quantity} × {self.food.name}"
        return f"{self.quantity} × [Item Removed]"

    @property
    def subtotal(self):
        return self.price * self.quantity

    @property
    def food_name(self):
        return self.food.name if self.food else "Item no longer available"