from urllib.parse import urlparse

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework import serializers

from apps.shop.models import (
    Product,
    ProductOption,
    ProductVariant,
    ProductImage,
    ProductVariantImage,
)


# class ProductOptionItemSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProductOptionItem
#         fields = ["id", "item_name"]


class ProductOptionSerializer(serializers.ModelSerializer):
    items = serializers.ListSerializer(child=serializers.CharField(), required=False)

    class Meta:
        model = ProductOption
        fields = ["id", "option_name", "items"]


class ProductVariantImageSerializer(serializers.ModelSerializer):
    image_id = serializers.IntegerField(source="product_image.id")
    src = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariantImage
        fields = ["image_id", "src"]

    def get_src(self, obj):
        request = self.context.get("request")
        if request is None:
            return None  # Handle the case where request is None

        domain = request.get_host()
        media_url = settings.MEDIA_URL  # The URL prefix for media files
        src = obj.product_image.src  # Relative URL of the image

        # Check if media_url already contains a domain
        if not urlparse(media_url).scheme:
            return f"http://{domain}{media_url}{src}"
        else:
            return f"{media_url}{src}"


class ProductVariantSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="product.id", read_only=True)
    option1 = serializers.CharField(
        source="option1.item_name", required=False, default=None, read_only=True
    )
    option2 = serializers.CharField(
        source="option2.item_name", required=False, default=None, read_only=True
    )
    option3 = serializers.CharField(
        source="option3.item_name", required=False, default=None, read_only=True
    )
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    images_id = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    images = ProductVariantImageSerializer(many=True, read_only=True)

    class Meta:
        model = ProductVariant
        fields = [
            "id",
            "product_id",
            "price",
            "stock",
            "sku",
            "option1",
            "option2",
            "option3",
            "images_id",
            "images",
            "created_at",
            "updated_at",
        ]


class ProductImageSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="product.id", read_only=True)
    images = serializers.ListField(
        child=serializers.ImageField(), required=False, default=None, write_only=True
    )
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = ProductImage
        fields = [
            "id",
            "product_id",
            "src",
            "alt",
            "is_main",
            "images",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["src", "alt", "created_at", "updated_at"]


class ProductCreateSerializer(serializers.ModelSerializer):
    status = serializers.CharField(
        max_length=10, allow_blank=True, required=False, default=Product.STATUS_DRAFT
    )
    stock = serializers.IntegerField(default=0, validators=[MinValueValidator(0)])
    price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        validators=[
            MinValueValidator(limit_value=0),
            MaxValueValidator(limit_value=9999999999.99),
        ],
    )
    # TODO write tests for sku field on API endpoints
    sku = serializers.CharField(
        max_length=250, allow_blank=True, required=False, default=""
    )
    options = ProductOptionSerializer(many=True, required=False, default=None)
    variants = ProductVariantSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "name",
            "slug",
            "description",
            "status",
            "price",
            "stock",
            "sku",
            "options",
            "variants",
            "created_at",
            "updated_at",
            "published_at",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
            "published_at",
        ]

    @staticmethod
    def validate_options(options):
        # If options is None, return None
        if not options:
            return None

        # Dictionary to store merged options
        merged_options = {}

        # Iterate through each option in the list
        for option in options:
            option_name = option.get("option_name")
            items = option.get("items")

            # Raise an error if 'items' is missing
            if items is None:
                raise serializers.ValidationError(
                    "Each option in 'options' must have a 'items'."
                )

            # If 'items' is not empty, update the merged_options dictionary
            if items:
                if option_name in merged_options:
                    merged_options[option_name].update(items)
                else:
                    merged_options[option_name] = set(items)

        # Create a list of unique options with sorted 'items'
        unique_options = [
            {"option_name": option_name, "items": list(items)}
            for option_name, items in merged_options.items()
        ]

        # Check if the number of unique options exceeds the limit
        if len(unique_options) > 3:
            raise serializers.ValidationError(
                "A product can have a maximum of 3 options."
            )

        # Sort option-names and item-names for use in comparing two dictionaries in `assertEqual` function in tests
        for option in unique_options:
            option["items"] = sorted(option["items"])
        unique_options = sorted(unique_options, key=lambda x: x["option_name"])
        return unique_options

    @staticmethod
    def validate_status(value):
        """Validate the 'status' field and return 'draft' if it is invalid or not set."""

        valid_statuses = [status[0] for status in Product.STATUS_CHOICES]
        if value not in valid_statuses:
            return Product.STATUS_DRAFT
        return value

    def to_representation(self, instance):
        product_serializer = ProductSerializer(instance)
        return product_serializer.data


class ProductUpdateSerializer(ProductCreateSerializer):
    pass


class ProductSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    published_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M:%S", required=False, read_only=True
    )
    options = ProductOptionSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, source="media", read_only=True)

    # TODO set these fields `variants_min_price`, `variants_max_price`, `variants_total_stock` at CRUD response body
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "status",
            "options",
            "variants",
            # "variants_min_price",
            # "variants_max_price",
            # "variants_total_stock",
            "images",
            "created_at",
            "updated_at",
            "published_at",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Check if the "options" field is an empty list and set it to None
        if not representation["options"]:
            representation["options"] = None
        if not representation["images"]:
            representation["images"] = None

        return representation
