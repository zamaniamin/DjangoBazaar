import uuid

from django.db import models

from apps.shop.models import Product


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid)
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="cart_items"
    )
    quantity = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = [["cart", "product"]]
