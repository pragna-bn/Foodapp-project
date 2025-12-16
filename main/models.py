from django.db import models
from django.contrib.auth.models import User
from restaurants.models import Restaurant


# --------------------------
# Category & Offer Models
# --------------------------
class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Offer(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)


    def __str__(self):
        return self.title


# --------------------------
# FoodItem Model
# --------------------------
class FoodItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name='foods'
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='food/', blank=True, null=True)

    # Optional fields
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True
    )
    offer = models.ForeignKey(
        Offer, on_delete=models.SET_NULL, null=True, blank=True
    )
    is_trending = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.restaurant.name})"

    @property
    def subtotal(self):
        return self.price


# --------------------------
# Orders Models
# --------------------------
class Order(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    total = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0
    )

    def __str__(self):
        return f"Order #{self.id} by {self.full_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='items'
    )
    food = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.food.name}"


# --------------------------
# Cart Model
# --------------------------
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.food_item.name} ({self.quantity})"


# --------------------------
# Favorite / Wishlist Model
# --------------------------
class FavoriteItem(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorites'
    )
    food_item = models.ForeignKey(
        FoodItem, on_delete=models.CASCADE, related_name='favorited_by'
    )

    class Meta:
        unique_together = ('user', 'food_item')

    def __str__(self):
        return f"{self.user.username} - {self.food_item.name}"