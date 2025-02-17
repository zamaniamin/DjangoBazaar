import uuid

from django.core.validators import MinValueValidator
from django.db import models

from apps.core.models.mixin import ModelMixin
from apps.shop.models.product import ProductVariant


class Cart(ModelMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.CASCADE, related_name="cart_items"
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        unique_together = [["cart", "variant"]]
