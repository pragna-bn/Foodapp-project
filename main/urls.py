from django.urls import path
from . import views

urlpatterns = [
    # HOME
    path('', views.home, name='home'),

    # SEARCH
    path('search/', views.search_food, name='search_food'),

    # FAVORITES
    path('favorites/', views.view_favorites, name='favorites'),
    path('favorites/add/<int:food_id>/', views.add_to_favorites, name='add_to_favorites'),
    path('favorites/remove/<int:food_id>/', views.remove_favorite, name='remove_favorite'),

    # CATEGORIES
    path('category/<int:category_id>/', views.foods_by_category, name='foods_by_category'),

    # BEST OFFERS (Correct)
    path('offer/<int:offer_id>/', views.foods_by_offer, name='foods_by_offer'),

    # CART 
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:food_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:food_id>/', views.remove_from_cart, name='remove_from_cart'),
    


]

