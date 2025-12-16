from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Restaurant
from orders.models import Order, OrderItem
from main.models import FoodItem

# ----------------------------
# List all restaurants
# ----------------------------
def restaurant_list(request):
    """
    Display all restaurants.
    """
    restaurants = Restaurant.objects.all()
    return render(request, 'restaurants/restaurant_list.html', {'restaurants': restaurants})

# ----------------------------
# Restaurant detail + foods
# ----------------------------
def restaurant_detail(request, pk):
    """
    Show details of a single restaurant, including its food items.
    """
    restaurant = get_object_or_404(Restaurant, pk=pk)
    
    # Fetch all FoodItems for this restaurant
    foods = FoodItem.objects.filter(restaurant=restaurant).order_by('name')

    # Get pending order if user is logged in
    pending_order = None
    if request.user.is_authenticated:
        pending_order = Order.objects.filter(user=request.user, status='PENDING').first()

    return render(request, 'restaurants/restaurant_detail.html', {
        'restaurant': restaurant,
        'foods': foods,
        'pending_order': pending_order
    })

# ----------------------------
# Add food to cart
# ----------------------------
@login_required
def add_to_cart(request, food_id):
    """
    Add a food item to the user's pending order (cart).
    """
    food = get_object_or_404(FoodItem, id=food_id)

    # Get or create pending order for user
    order, _ = Order.objects.get_or_create(
        user=request.user, status='PENDING', defaults={'total_price': 0}
    )

    # Add or update OrderItem
    order_item, created = OrderItem.objects.get_or_create(
        order=order,
        food=food,
        defaults={'price': food.price, 'quantity': 1}
    )

    if not created:
        order_item.quantity += 1
        order_item.save()

    # Update total price of order
    order.total_price = sum(item.subtotal for item in order.items.all())
    order.save()

    messages.success(request, f"{food.name} added to cart!")
    return redirect('restaurant_detail', pk=food.restaurant.pk)

# ----------------------------
# Order now (single item checkout) — UPDATED
# ----------------------------
@login_required
def order_now(request, food_id):
    """
    Place an immediate order for a single food item with customer details.
    """
    food = get_object_or_404(FoodItem, id=food_id)

    if request.method == "POST":
        # Save customer details from form
        customer_name = request.POST.get("customer_name")
        customer_phone = request.POST.get("customer_phone")
        customer_address = request.POST.get("customer_address")

        # Create completed order
        order = Order.objects.create(
            user=request.user,
            status='COMPLETED',
            total_price=food.price,
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_address=customer_address,
        )

        # Create Order Item
        OrderItem.objects.create(
            order=order,
            food=food,
            quantity=1,
            price=food.price
        )

        messages.success(request, f"{food.name} ordered successfully!")
        return redirect('my_orders')

    return render(request, 'restaurants/order_now.html', {'food': food})