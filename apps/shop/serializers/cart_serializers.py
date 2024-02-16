from rest_framework import serializers

from apps.shop.models import ProductVariant
from apps.shop.models.cart import CartItem, Cart


class CartVariantSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="product.id")
    option1 = serializers.CharField(
        source="option1.item_name", required=False, default=None, read_only=True
    )
    option2 = serializers.CharField(
        source="option2.item_name", required=False, default=None, read_only=True
    )
    option3 = serializers.CharField(
        source="option3.item_name", required=False, default=None, read_only=True
    )

    class Meta:
        model = ProductVariant
        fields = ["id", "product_id", "price", "stock", "option1", "option2", "option3"]


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["quantity"]


class AddCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["id", "variant", "quantity"]


class CartItemSerializer(serializers.ModelSerializer):
    variant = CartVariantSerializer()
    image = serializers.SerializerMethodField()
    item_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ["id", "variant", "image", "quantity", "item_total"]

    @staticmethod
    def get_image(cart_item) -> str | None:
        first_media = cart_item.variant.product.media.first()
        return first_media.src.url if first_media else None

    @staticmethod
    def get_item_total(cart_item) -> float:
        return cart_item.quantity * cart_item.variant.price


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "items", "total_price"]
        read_only_fields = [
            "id",
        ]

    @staticmethod
    def get_total_price(cart) -> float:
        return sum([item.quantity * item.variant.price for item in cart.items.all()])
