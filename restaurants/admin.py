from django.contrib import admin
from .models import Restaurant
from main.models import FoodItem

# Inline to show FoodItems under each Restaurant
class FoodItemInline(admin.TabularInline):
    model = FoodItem
    extra = 1  # show 1 blank row for adding new items
    fields = ('name', 'price', 'description', 'category', 'offer', 'image')  # all editable fields
    # remove readonly_fields so you can edit name and price

# Register Restaurant with inline
@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "is_popular")
    list_filter = ("is_popular",)
    search_fields = ("name", "location")
    inlines = [FoodItemInline]  # attach the FoodItems inline

