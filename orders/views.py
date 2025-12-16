from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order, OrderItem
from main.models import FoodItem

# ----------------------------
# View Cart
# ----------------------------
@login_required
def view_cart(request):
    order = Order.objects.filter(user=request.user, status='PENDING').first()
    items = order.items.all() if order else []
    total = order.total_price if order else 0
    return render(request, 'orders/cart.html', {
        'order': order,
        'items': items,
        'total': total
    })


# ----------------------------
# Remove from Cart
# ----------------------------
@login_required
def remove_from_cart(request, food_id):
    order = Order.objects.filter(user=request.user, status='PENDING').first()
    if order:
        item = OrderItem.objects.filter(order=order, food_id=food_id).first()
        if item:
            item.delete()
            order.save()
            messages.info(request, "Item removed from cart!")
    return redirect('view_cart')


# ----------------------------
# Increment Quantity
# ----------------------------
@login_required
def increment_quantity(request, food_id):
    order = Order.objects.filter(user=request.user, status='PENDING').first()
    if order:
        item = OrderItem.objects.filter(order=order, food_id=food_id).first()
        if item:
            item.quantity += 1
            item.save()
            order.save()
    return redirect('view_cart')


# ----------------------------
# Decrement Quantity
# ----------------------------
@login_required
def decrement_quantity(request, food_id):
    order = Order.objects.filter(user=request.user, status='PENDING').first()
    if order:
        item = OrderItem.objects.filter(order=order, food_id=food_id).first()
        if item:
            if item.quantity > 1:
                item.quantity -= 1
                item.save()
            else:
                item.delete()
            order.save()
    return redirect('view_cart')


# ----------------------------
# Checkout (Cart Checkout)
# ----------------------------
@login_required
def checkout(request):
    order = Order.objects.filter(user=request.user, status='PENDING').first()

    if not order:
        messages.error(request, "Your cart is empty!")
        return redirect('view_cart')

    items = order.items.all()
    total = order.total_price

    # GET → show customer details form
    if request.method == "GET":
        return render(request, "restaurants/checkout.html", {
            "order": order,
            "items": items,
            "total": total
        })

    # POST → save customer details and place order
    if request.method == "POST":
        order.customer_name = request.POST.get("customer_name")
        order.customer_phone = request.POST.get("customer_phone")
        order.customer_address = request.POST.get("customer_address")

        order.status = "PREPARING"
        order.save()

        messages.success(request, "Order placed successfully!")
        return redirect("my_orders")


# ----------------------------
# My Orders
# ----------------------------
@login_required
def my_orders(request):
    pending_order = Order.objects.filter(user=request.user, status='PENDING').first()
    orders = Order.objects.filter(user=request.user).exclude(status='PENDING')
    return render(request, 'orders/my_orders.html', {
        'pending_order': pending_order,
        'orders': orders
    })


# ----------------------------
# Cancel Order
# ----------------------------
@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if not order.can_cancel:
        messages.error(request, "This order cannot be cancelled!")
        return redirect('my_orders')

    order.status = 'CANCELLED'
    order.save()
    messages.success(request, "Order cancelled successfully!")
    return redirect('my_orders')


# ----------------------------
# Order Detail Page
# ----------------------------
@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = order.items.all()

    return render(request, "orders/order_detail.html", {
        "order": order,
        "items": items
    })