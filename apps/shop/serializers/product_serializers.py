from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework import serializers

from apps.shop.models import Product, ProductOption, ProductOptionItem, ProductVariant


class ProductOptionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductOptionItem
        fields = ['id', 'item_name']


class ProductOptionSerializer(serializers.ModelSerializer):
    items = serializers.ListSerializer(child=serializers.CharField(), source='productoptionitem_set', required=False)

    class Meta:
        model = ProductOption
        fields = ['id', 'option_name', 'items']


class ProductCreateSerializer(serializers.ModelSerializer):
    options = ProductOptionSerializer(many=True, required=False, default=None)
    status = serializers.CharField(max_length=10, allow_blank=True, required=False)
    stock = serializers.IntegerField(default=0, validators=[MinValueValidator(0)])
    price = serializers.DecimalField(
        max_digits=12, decimal_places=2, default=0.00,
        validators=[MinValueValidator(limit_value=0), MaxValueValidator(limit_value=9999999999.99)])

    class Meta:
        model = Product
        fields = ['product_name', 'description', 'status', 'price', 'stock', 'options']

    def validate_options(self, options):
        """
        Merge dictionaries with the same "option_name" and make the "items" unique.
        Remove options with an empty "items" list.
        Check max 3 options per product.
        """

        if options is None:
            return None

        merged_options = {}

        for option in options:
            option_name = option['option_name']
            items = option['productoptionitem_set']

            if items:
                if option_name in merged_options:
                    merged_options[option_name].update(items)
                else:
                    merged_options[option_name] = set(items)

        unique_options = [
            {"option_name": option_name, "items": list(items)}
            for option_name, items in merged_options.items()
        ]
        if len(unique_options) > 3:
            raise serializers.ValidationError("A product can have a maximum of 3 options.")

        # I need to sort option-names and item-names, for use to compare two dict in `assertEqual` function in the tests
        for option in unique_options:
            option['items'] = sorted(option['items'])
        unique_options = sorted(unique_options, key=lambda x: x['option_name'])
        return unique_options

    def validate_status(self, value):
        """
        Validate the "status" field and return `draft` if it is invalid or not set
        """
        valid_statuses = [status[0] for status in Product.STATUS_CHOICES]
        if value not in valid_statuses:
            return 'draft'
        return value


class ProductVariantSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    updated_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    option1 = serializers.CharField(source='option1.item_name', required=False)
    option2 = serializers.CharField(source='option2.item_name', required=False)
    option3 = serializers.CharField(source='option3.item_name', required=False)

    class Meta:
        model = ProductVariant
        fields = ['id', 'price', 'stock', 'option1', 'option2', 'option3', 'created_at', 'updated_at']


class ProductSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    updated_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    published_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False)
    options = ProductOptionSerializer(many=True, source='productoption_set')
    variants = ProductVariantSerializer(many=True, source='productvariant_set')

    class Meta:
        model = Product
        fields = ['id', 'product_name', 'description', 'status', 'options', 'variants', 'created_at', 'updated_at',
                  'published_at']
