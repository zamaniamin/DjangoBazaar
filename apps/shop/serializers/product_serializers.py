from urllib.parse import urlparse

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework import serializers

from apps.core.serializers.mixin import ModelMixinSerializer
from apps.shop.models.attribute import Attribute, AttributeItem
from apps.shop.models.category import Category
from apps.shop.models.product import (
    Product,
    ProductOption,
    ProductVariant,
    ProductImage,
    ProductVariantImage,
)


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


class ProductVariantSerializer(ModelMixinSerializer):
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


class ProductImageSerializer(ModelMixinSerializer):
    product_id = serializers.IntegerField(source="product.id", read_only=True)
    images = serializers.ListField(
        child=serializers.ImageField(), required=False, default=None, write_only=True
    )

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


class ProductAttributeInputSerializer(serializers.Serializer):
    attribute_id = serializers.IntegerField()
    items_id = serializers.ListField(child=serializers.IntegerField())


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
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), required=False, allow_null=True
    )
    attributes = ProductAttributeInputSerializer(
        many=True, required=False, default=list
    )

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
            "category",
            "attributes",
            "created_at",
            "updated_at",
            "published_at",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
            "published_at",
        ]

    def validate_attributes(self, attributes):
        for attr in attributes:
            attribute_id = attr["attribute_id"]
            item_ids = attr["items_id"]

            # Validate attribute ID
            if not Attribute.objects.filter(id=attribute_id).exists():
                raise serializers.ValidationError(
                    f"One or more attribute IDs are invalid."
                )

            # Validate item IDs
            valid_item_ids = AttributeItem.objects.filter(
                attribute_id=attribute_id
            ).values_list("id", flat=True)
            invalid_item_ids = [
                item_id for item_id in item_ids if item_id not in valid_item_ids
            ]

            if invalid_item_ids:
                raise serializers.ValidationError(
                    f"Item IDs {invalid_item_ids} are invalid for attribute ID {attribute_id}."
                )

        return attributes

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


class ProductSerializer(ModelMixinSerializer):
    DEFAULT_TOTAL_STOCK = 0

    published_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M:%S", required=False, read_only=True
    )
    options = ProductOptionSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, source="media", read_only=True)

    price = serializers.SerializerMethodField(read_only=True)
    total_stock = serializers.IntegerField(read_only=True)
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), required=False, allow_null=True
    )
    attributes = serializers.SerializerMethodField(read_only=True)

    # TODO set these fields `price`, `total_stock`, `category`, at CRUD response body
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
            "category",
            "attributes",
            "price",
            "total_stock",
            "images",
            "created_at",
            "updated_at",
            "published_at",
        ]

    def get_price(self, instance):
        # Use annotated values instead of querying variants
        return {
            "min_price": getattr(instance, "min_price", None),
            "max_price": getattr(instance, "max_price", None),
        }

    def get_attributes(self, instance):
        """
        Return the attributes associated with the product.
        If there are no attributes, return None.
        """
        attributes = []
        for product_attribute in instance.productattribute_set.all():
            attribute = product_attribute.attribute
            selected_items = product_attribute.items.all()
            attributes.append(
                {
                    "attribute_id": attribute.id,
                    "attribute_name": attribute.attribute_name,
                    "items": [
                        {
                            "item_id": item.id,
                            "item_name": item.item_name,
                        }
                        for item in selected_items
                    ],
                }
            )
        return attributes if attributes else None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        self._set_none_if_empty(representation, "options")
        self._set_none_if_empty(representation, "images")
        representation["total_stock"] = getattr(
            instance, "total_stock", self.DEFAULT_TOTAL_STOCK
        )

        return representation

    @staticmethod
    def _set_none_if_empty(data, field_name):
        """Helper to set a field to None if it's empty."""
        if not data.get(field_name):
            data[field_name] = None
