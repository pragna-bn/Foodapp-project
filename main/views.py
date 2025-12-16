from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import (
    Restaurant,
    FoodItem,
    CartItem,
    Order,
    FavoriteItem,
    Category,
    Offer
)


# -------------------------
# HOME PAGE
# -------------------------
def home(request):
    trending_foods = FoodItem.objects.filter(is_trending=True)[:6]
    popular_restaurants = Restaurant.objects.filter(is_popular=True)[:6]
    categories = Category.objects.all()[:10]
    offers = Offer.objects.all()[:6]

    return render(request, 'main/home.html', {
        'trending_foods': trending_foods,
        'popular_restaurants': popular_restaurants,
        'categories': categories,
        'offers': offers,
    })


# -------------------------
# RESTAURANT LIST
# -------------------------
def restaurant_list(request):
    restaurants = Restaurant.objects.all()
    return render(request, 'main/restaurant_list.html', {'restaurants': restaurants})


# -------------------------
# RESTAURANT DETAIL
# -------------------------
def restaurant_detail(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)
    foods = FoodItem.objects.filter(restaurant=restaurant)

    return render(request, 'main/restaurant_detail.html', {
        'restaurant': restaurant,
        'foods': foods
    })


# -------------------------
# FOODS BY CATEGORY
# -------------------------
def foods_by_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    foods = FoodItem.objects.filter(category=category)

    return render(request, 'main/category_foods.html', {
        'category': category,
        'foods': foods
    })


# -------------------------
# FOODS BY OFFER
# -------------------------
def foods_by_offer(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    foods = FoodItem.objects.filter(offer=offer)

    return render(request, 'main/offer_foods.html', {
        'offer': offer,
        'foods': foods
    })


# -------------------------
# ADD TO CART
# -------------------------
@login_required(login_url='login')
def add_to_cart(request, food_id):
    food = get_object_or_404(FoodItem, id=food_id)

    cart_item, created = CartItem.objects.get_or_create(
        food_item=food,
        user=request.user
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('view_cart')


# -------------------------
# VIEW CART (WITH OFFER LOGIC)
# -------------------------
@login_required(login_url='login')
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)

    total_price = 0
    for item in cart_items:
        item.subtotal = item.food_item.price * item.quantity
        total_price += item.subtotal

    # 🔥 Auto apply best offer
    applied_offer = None
    discount = 0

    offer = Offer.objects.filter(is_active=True).order_by('-discount_amount').first()
    if offer and total_price >= offer.min_order_amount:
        discount = offer.discount_amount
        applied_offer = offer

    final_total = total_price - discount

    return render(request, 'main/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'discount': discount,
        'final_total': final_total,
        'applied_offer': applied_offer,
    })


# -------------------------
# INCREMENT CART ITEM
# -------------------------
@login_required(login_url='login')
def increment_quantity(request, food_id):
    cart_item = get_object_or_404(
        CartItem, user=request.user, food_item_id=food_id
    )
    cart_item.quantity += 1
    cart_item.save()
    return redirect('view_cart')


# -------------------------
# DECREMENT CART ITEM
# -------------------------
@login_required(login_url='login')
def decrement_quantity(request, food_id):
    cart_item = get_object_or_404(
        CartItem, user=request.user, food_item_id=food_id
    )

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()

    return redirect('view_cart')


# -------------------------
# REMOVE CART ITEM
# -------------------------
@login_required(login_url='login')
def remove_from_cart(request, food_id):
    cart_item = get_object_or_404(
        CartItem, user=request.user, food_item_id=food_id
    )
    cart_item.delete()
    return redirect('view_cart')


# -------------------------
# PLACE ORDER (WITH OFFER)
# -------------------------
@login_required(login_url='login')
def place_order(request):
    cart_items = CartItem.objects.filter(user=request.user)

    if not cart_items:
        return redirect('view_cart')

    total_price = sum(
        item.food_item.price * item.quantity for item in cart_items
    )

    applied_offer = None
    discount = 0

    offer = Offer.objects.filter(is_active=True).order_by('-discount_amount').first()
    if offer and total_price >= offer.min_order_amount:
        discount = offer.discount_amount
        applied_offer = offer

    final_total = total_price - discount

    order = Order.objects.create(
        total=final_total,
        applied_offer=applied_offer,
        discount=discount
    )

    for item in cart_items:
        order.items.create(
            food=item.food_item,
            quantity=item.quantity,
            subtotal=item.food_item.price * item.quantity
        )

    cart_items.delete()
    messages.success(request, "Order placed successfully!")
    return redirect('my_orders')


# -------------------------
# MY ORDERS
# -------------------------
@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.order_by('-created_at')
    return render(request, 'main/my_orders.html', {'orders': orders})


# -------------------------
# CANCEL ORDER
# -------------------------
@login_required(login_url='login')
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = "CANCELLED"
    order.save()
    return redirect('my_orders')


# -------------------------
# SEARCH FOOD
# -------------------------
def search_food(request):
    query = request.GET.get('q', '')
    results = FoodItem.objects.filter(name__icontains=query)

    return render(request, 'main/search_results.html', {
        'query': query,
        'results': results
    })


# =====================================================
# FAVORITES (WISHLIST)
# =====================================================
@login_required(login_url='login')
def add_to_favorites(request, food_id):
    food = get_object_or_404(FoodItem, id=food_id)
    FavoriteItem.objects.get_or_create(user=request.user, food_item=food)
    messages.success(request, f"{food.name} added to Favorites!")
    return redirect(request.META.get('HTTP_REFERER', 'restaurant_list'))


@login_required(login_url='login')
def remove_favorite(request, food_id):
    food = get_object_or_404(FoodItem, id=food_id)
    FavoriteItem.objects.filter(user=request.user, food_item=food).delete()
    messages.success(request, f"{food.name} removed from Favorites!")
    return redirect('favorites')


@login_required(login_url='login')
def view_favorites(request):
    favorites = FavoriteItem.objects.filter(user=request.user)
    return render(request, "main/favorites.html", {"favorites": favorites})