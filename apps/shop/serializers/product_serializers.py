from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework import serializers

from apps.shop.models import Product, ProductOption, ProductOptionItem, ProductVariant


class ProductOptionItemSerializer(serializers.ModelSerializer):
    """
    Serializer for the ProductOptionItem model.

    Attributes:
    - id (IntegerField): Unique identifier for the product option item.
    - item_name (CharField): Display name of the product option item.

    """

    class Meta:
        model = ProductOptionItem
        fields = ["id", "item_name"]


class ProductOptionSerializer(serializers.ModelSerializer):
    """
    Serializer for the ProductOption model.

    Attributes:
    - id (IntegerField): Unique identifier for the product option.
    - option_name (CharField): Display name of the product option.
    - items (ListSerializer of CharField, optional): List of item names associated with the product option.

    """

    items = serializers.ListSerializer(
        child=serializers.CharField(), source="productoptionitem_set", required=False
    )

    class Meta:
        model = ProductOption
        fields = ["id", "option_name", "items"]


class ProductVariantSerializer(serializers.ModelSerializer):
    """
    Serializer for the ProductVariant model.

    Attributes:
    - created_at (DateTimeField): Formatted representation of the variant creation timestamp.
    - updated_at (DateTimeField): Formatted representation of the variant update timestamp.
    - option1 (CharField, optional): Display name of the first product option.
    - option2 (CharField, optional): Display name of the second product option.
    - option3 (CharField, optional): Display name of the third product option.

    """

    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    option1 = serializers.CharField(
        source="option1.item_name", required=False, default=None
    )
    option2 = serializers.CharField(
        source="option2.item_name", required=False, default=None
    )
    option3 = serializers.CharField(
        source="option3.item_name", required=False, default=None
    )

    class Meta:
        model = ProductVariant
        fields = [
            "id",
            "price",
            "stock",
            "option1",
            "option2",
            "option3",
            "created_at",
            "updated_at",
        ]


class ProductCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new Product instance.

    Attributes:
    - options (list of dict): A list containing dictionaries with 'option_name' and 'productoptionitem_set'.
    - status (str): The status of the product.
    - stock (int): The stock quantity of the product.
    - price (Decimal): The price of the product.

    """

    status = serializers.CharField(
        max_length=10, allow_blank=True, required=False, default="draft"
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
    options = ProductOptionSerializer(many=True, required=False, default=None)
    variants = ProductVariantSerializer(
        many=True, source="productvariant_set", read_only=True
    )

    class Meta:
        model = Product
        fields = [
            "product_name",
            "description",
            "status",
            "price",
            "stock",
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
        """
        Validate and process the 'options' field.

        Explanation:
        - Merge dictionaries with the same 'option_name' and make the 'items' unique.
        - Remove options with an empty 'items' list.
        - Check maximum 3 options per product.

        Args:
        - options (list of dict): A list containing dictionaries with 'option_name' and 'productoptionitem_set'.

        Returns:
        - list of dict: A processed and validated list of unique options.

        Raises:
        - serializers.ValidationError: If the number of options exceeds the limit.

        """

        # If options is None, return None
        if not options:
            return None

        # Dictionary to store merged options
        merged_options = {}

        # Iterate through each option in the list
        for option in options:
            option_name = option.get("option_name")
            items = option.get("productoptionitem_set")

            # Raise an error if 'productoptionitem_set' is missing
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
        """
        Validate the 'status' field and return 'draft' if it is invalid or not set.

        Args:
        - value (str): The status value to be validated.

        Returns:
        - str: The validated status value.

        """
        valid_statuses = [status[0] for status in Product.STATUS_CHOICES]
        if value not in valid_statuses:
            return "draft"
        return value


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for the Product model.

    Attributes:
    - created_at (DateTimeField): Formatted representation of the product creation timestamp.
    - updated_at (DateTimeField): Formatted representation of the product update timestamp.
    - published_at (DateTimeField, optional): Formatted representation of the product publish timestamp.
    - options (ProductOptionSerializer): Serializer for the product options.
    - variants (ProductVariantSerializer): Serializer for the product variants.

    """

    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    published_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)
    options = ProductOptionSerializer(many=True, source="productoption_set")
    variants = ProductVariantSerializer(many=True, source="productvariant_set")

    class Meta:
        model = Product
        fields = [
            "id",
            "product_name",
            "description",
            "status",
            "options",
            "variants",
            "created_at",
            "updated_at",
            "published_at",
        ]
        read_only_fields = [
            "options",
            "variants",
            "created_at",
            "updated_at",
            "published_at",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Check if the "options" field is an empty list and set it to None
        if not representation["options"]:
            representation["options"] = None

        return representation
