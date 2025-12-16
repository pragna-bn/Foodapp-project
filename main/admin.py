from django.contrib import admin
from .models import FoodItem, Category, Offer, CartItem, Order, FavoriteItem

class FoodItemAdmin(admin.ModelAdmin): list_display = ('name', 'category', 'price', 'is_trending')
list_filter = ('is_trending',)
search_fields = ('name',)


admin.site.register(FoodItem, FoodItemAdmin)
admin.site.register(Category)
admin.site.register(Offer)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(FavoriteItem)