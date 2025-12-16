from django import template
from main.models import FavoriteItem, FoodItem

register = template.Library()

@register.filter
def user_has_favorite(food, user):
    # Food must be a FoodItem instance
    if not isinstance(food, FoodItem):
        return False

    if not user.is_authenticated:
        return False
    
    return FavoriteItem.objects.filter(food_item=food, user=user).exists()