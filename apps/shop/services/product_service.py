from itertools import product as options_combination

from django.db.models import Prefetch

from apps.core.services.time_service import DateTime
from apps.shop.models.product import Product, ProductOption, ProductOptionItem, ProductVariant


class ProductService:
    product = None
    price: int | float
    stock: int
    options: list | None = []
    options_data: list = []
    variants: list = []
    media: list | None = None

    @classmethod
    def create_product(cls, **data):
        """
        Create a new product with options and return the product object.

        Args:
            **data: Keyword arguments containing product data, including 'price', 'stock', and 'options'.

        Returns:
            Product: The created product object.

        Note:
            This method creates a new product instance, generates options, and optimizes queries
            for retrieving the product with related options and variants.
        """

        # Extract relevant data
        cls.price = data.pop('price')
        cls.stock = data.pop('stock')
        cls.options_data = data.pop('options')

        # Create product
        cls.product = Product.objects.create(**data)

        # Create options
        cls.__create_product_options()

        # Return product object with optimized queries
        select_related_variant_options = ProductVariant.objects.select_related('option1', 'option2', 'option3')
        prefetch_variants = Prefetch('productvariant_set', queryset=select_related_variant_options)
        prefetch_product = Product.objects.prefetch_related('productoption_set__productoptionitem_set',
                                                            prefetch_variants)
        return prefetch_product.get(pk=cls.product.id)

    @classmethod
    def __create_product_options(cls):
        """
        Create new option if it doesn't exist and update its items.
        """

        if cls.options_data:
            options_to_create = []
            items_to_create = []

            for option in cls.options_data:
                new_option = ProductOption(product=cls.product, option_name=option['option_name'])
                options_to_create.append(new_option)

                for item in option['items']:
                    new_item = ProductOptionItem(option=new_option, item_name=item)
                    items_to_create.append(new_item)

            ProductOption.objects.bulk_create(options_to_create)
            ProductOptionItem.objects.bulk_create(items_to_create)

            cls.__create_product_variants(bulk_create=True)
        else:
            cls.options = None

    @classmethod
    def __create_product_variants(cls, bulk_create: bool = False):
        """
        Create a default variant or create variants by options combination.
        """

        if bulk_create:
            items_id = cls.__get_item_ids_by_product_id(cls.product.id)
            variants = list(options_combination(*items_id))
            variants_to_create = []

            for variant in variants:
                values_tuple = tuple(variant)

                while len(values_tuple) < 3:
                    values_tuple += (None,)
                option1, option2, option3 = values_tuple

                new_variant = ProductVariant(
                    product=cls.product,
                    option1_id=option1,
                    option2_id=option2,
                    option3_id=option3,
                    price=cls.price,
                    stock=cls.stock
                )
                variants_to_create.append(new_variant)

            ProductVariant.objects.bulk_create(variants_to_create)
        else:
            ProductVariant.objects.create(product=cls.product, price=cls.price, stock=cls.stock)

    @staticmethod
    def __get_item_ids_by_product_id(product_id):

        item_ids_by_option = []

        # Query the ProductOptionItem table to retrieve item_ids
        items = (
            ProductOptionItem.objects
            .filter(option__product_id=product_id)
            .values_list('option_id', 'id')
        )

        # Group item_ids by option_id
        item_ids_dict = {}
        for option_id, item_id in items:
            item_ids_dict.setdefault(option_id, []).append(item_id)

        # Append `item_ids` lists to the result list
        item_ids_by_option.extend(item_ids_dict.values())

        return item_ids_by_option

    @staticmethod
    def retrieve_options(product_id):
        """
        Get all options of a product
        """
        # TODO return an object not list

        product_options = []

        # Fetch ProductOption and related ProductOptionItem objects in a single query
        options = ProductOption.objects.select_related('product').prefetch_related('productoptionitem_set').filter(
            product=product_id)

        for option in options:
            items = option.productoptionitem_set.all()

            product_options.append({
                'option_id': option.id,
                'option_name': option.option_name,
                'items': [{'item_id': item.id, 'item_name': item.item_name} for item in items]
            })

        if product_options:
            return product_options
        else:
            return None

    @classmethod
    def retrieve_variants(cls, product_id):
        """
        Get all variants of a product
        """
        # TODO return an object not list

        product_variants = []
        variants: list[ProductVariant] = (
            ProductVariant.objects
            .filter(product=product_id)
            .select_related('option1', 'option2', 'option3')
        )
        for variant in variants:
            product_variants.append({
                "variant_id": variant.id,
                "product_id": variant.product_id,
                "price": variant.price,
                "stock": variant.stock,
                "option1": variant.option1.item_name if variant.option1 else None,
                "option2": variant.option2.item_name if variant.option2 else None,
                "option3": variant.option3.item_name if variant.option3 else None,
                "created_at": DateTime.string(variant.created_at),
                "updated_at": DateTime.string(variant.updated_at)
            })

        if product_variants:
            return product_variants
        return None
