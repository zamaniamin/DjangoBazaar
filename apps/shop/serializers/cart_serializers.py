from rest_framework import serializers

from apps.shop.models import ProductVariant
from apps.shop.models.cart import CartItem, Cart


class CartVariantSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="product.id")

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

    def create(self, validated_data):
        cart_id = self.context["cart_pk"]

        variant = validated_data.get("variant")
        quantity = validated_data.get("quantity")

        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, variant_id=variant.id)
            cart_item.quantity += quantity
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(cart_id=cart_id, **validated_data)

        self.instance = cart_item
        return cart_item


class CartItemSerializer(serializers.ModelSerializer):
    variant = CartVariantSerializer()
    item_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ["id", "variant", "quantity", "item_total"]

    def get_item_total(self, cart_item):
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

    def get_total_price(self, cart):
        return sum([item.quantity * item.variant.price for item in cart.items.all()])
