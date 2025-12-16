from django.urls import path
from . import views

urlpatterns = [
    path('', views.restaurant_list, name='restaurant_list'),
    path('<int:pk>/', views.restaurant_detail, name='restaurant_detail'),
    path('order-now/<int:food_id>/', views.order_now, name='order-now'),  # for Order Now button
    path('add-to-cart/<int:food_id>/', views.add_to_cart, name='add_to_cart'),  # existing
]