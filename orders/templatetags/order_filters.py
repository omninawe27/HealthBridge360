from django import template
from ..services import CartService

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.simple_tag
def get_cart_count(user):
    """Get the cart item count for a user"""
    if user.is_authenticated:
        try:
            cart = CartService.get_or_create_cart(user)
            return cart.item_count
        except:
            return 0
    return 0
