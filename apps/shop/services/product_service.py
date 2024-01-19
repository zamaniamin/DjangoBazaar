from itertools import product as options_combination

from django.db.models import Prefetch
from django.utils import timezone

from apps.core.services.time_service import DateTime
from apps.shop.models.product import (
    Product,
    ProductOption,
    ProductOptionItem,
    ProductVariant,
    ProductMedia,
)


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
        cls.price = data.pop("price")
        cls.stock = data.pop("stock")
        cls.options_data = data.pop("options")

        if data["status"] == Product.STATUS_ACTIVE:
            data["published_at"] = timezone.now()

        # Create product
        cls.product = Product.objects.create(**data)

        # Create options
        cls.__create_product_options()

        # Return product object
        return cls.retrieve_product_details(cls.product.id)

    @classmethod
    def create_product_images(cls, product_id, **data):
        images = ProductMedia.objects.bulk_create(
            [
                ProductMedia(product_id=product_id, src=image_data)
                for image_data in data["images"]
            ]
        )
        return images

    @staticmethod
    def retrieve_product_details(product_id):
        """
        Retrieve and return product details with optimized queries.

        Args:
            product_id (int): The ID of the product to retrieve.

        Returns:
            Product: The product object with related options and variants.

        Note:
            This method retrieves a specific product along with its associated options and variants,
            optimizing queries to minimize database round-trips for improved performance.

        """
        select_related_variant_options = ProductVariant.objects.select_related(
            "option1", "option2", "option3"
        )

        prefetch_variants = Prefetch(
            "variants", queryset=select_related_variant_options
        )

        prefetch_related_product_data = Product.objects.prefetch_related(
            "options__items", prefetch_variants
        ).prefetch_related("media")

        return prefetch_related_product_data.get(pk=product_id)

    @classmethod
    def __create_product_options(cls):
        """
        Create product options and associated items.

        Explanation:
        If cls.options_data is provided, it creates ProductOption and ProductOptionItem instances
        based on the data provided. It then calls __create_product_variants to generate and create
        product variants based on the product options.

        Note:
        This method assumes that cls.product, cls.options_data, and cls.__create_product_variants are set
        appropriately before calling.

        """
        if cls.options_data:
            options_to_create = []
            items_to_create = []

            for option in cls.options_data:
                # Create a ProductOption instance for each option_name
                new_option = ProductOption(
                    product=cls.product, option_name=option["option_name"]
                )
                options_to_create.append(new_option)

                for item in option["items"]:
                    # Create a ProductOptionItem instance for each item
                    new_item = ProductOptionItem(option=new_option, item_name=item)
                    items_to_create.append(new_item)

            # Bulk create the product options and items in the database
            ProductOption.objects.bulk_create(options_to_create)
            ProductOptionItem.objects.bulk_create(items_to_create)

            # generate and create product variants
            cls.__create_product_variants(bulk_create=True)
        else:
            # If no options_data is provided, set cls.options to None
            cls.__create_product_variants()
            cls.options = None

    @classmethod
    def __create_product_variants(cls, bulk_create: bool = False):
        """
        Create product variants based on product options.

        Parameters:
        - bulk_create (bool): If True, use bulk_create to efficiently create variants in bulk.

        Explanation:
        If bulk_create is set to True, it generates all possible combinations of product options,
        creates ProductVariant instances for each combination, and bulk creates them in the database.
        If bulk_create is False, it creates a single ProductVariant instance for the product.

        Note:
        This method assumes that cls.product, cls.price, and cls.stock are set appropriately before calling.

        """
        if bulk_create:
            # Retrieve the IDs of the product options associated with the product
            items_id = cls.__get_item_ids_by_product_id(cls.product.id)

            # Generate all possible combinations of product options
            variants = list(options_combination(*items_id))
            variants_to_create = []

            for variant in variants:
                values_tuple = tuple(variant)

                # Ensure the tuple has three elements (option1, option2, option3)
                while len(values_tuple) < 3:
                    values_tuple += (None,)
                option1, option2, option3 = values_tuple

                # Create a ProductVariant instance for each combination
                new_variant = ProductVariant(
                    product=cls.product,
                    option1_id=option1,
                    option2_id=option2,
                    option3_id=option3,
                    price=cls.price,
                    stock=cls.stock,
                )
                variants_to_create.append(new_variant)

            # Bulk create the variants in the database
            ProductVariant.objects.bulk_create(variants_to_create)
        else:
            # Create a single ProductVariant instance for the product
            ProductVariant.objects.create(
                product=cls.product, price=cls.price, stock=cls.stock
            )

    @staticmethod
    def __get_item_ids_by_product_id(product_id):
        """
        Get item_ids grouped by option_id for a given product_id.

        Explanation: This method queries the ProductOptionItem table to retrieve item_ids associated with a given
        product_id. It groups the item_ids by option_id and returns a list of lists where each sublist contains
        item_ids for a specific option.

        Args:
        - product_id (int): The ID of the product for which to retrieve item_ids.

        Returns:
        List[List[int]]: A list of lists where each sublist contains item_ids for a specific option.

        """
        item_ids_by_option = []

        # Query the ProductOptionItem table to retrieve item_ids
        items = ProductOptionItem.objects.filter(
            option__product_id=product_id
        ).values_list("option_id", "id")

        # Group item_ids by option_id
        item_ids_dict = {}
        for option_id, item_id in items:
            item_ids_dict.setdefault(option_id, []).append(item_id)

        # Append `item_ids` lists to the result list
        item_ids_by_option.extend(item_ids_dict.values())

        return item_ids_by_option

    @staticmethod
    def retrieve_options(product_id):
        # TODO remove this method after add endpoint for options
        """
        Get all options of a product
        """
        # TODO return an object not list

        product_options = []

        # Fetch ProductOption and related ProductOptionItem objects in a single query
        options = (
            ProductOption.objects.select_related("product")
            .prefetch_related("items")
            .filter(product=product_id)
        )

        for option in options:
            items = option.items.all()

            product_options.append(
                {
                    "option_id": option.id,
                    "option_name": option.option_name,
                    "items": [
                        {"item_id": item.id, "item_name": item.item_name}
                        for item in items
                    ],
                }
            )

        if product_options:
            return product_options
        else:
            return None

    @classmethod
    def retrieve_variants(cls, product_id):
        # TODO remove this method after add endpoint for variants
        """
        Get all variants of a product
        """
        # TODO return an object not list

        product_variants = []
        variants: list[ProductVariant] = ProductVariant.objects.filter(
            product=product_id
        ).select_related("option1", "option2", "option3")
        for variant in variants:
            product_variants.append(
                {
                    "variant_id": variant.id,
                    "product_id": variant.product_id,
                    "price": variant.price,
                    "stock": variant.stock,
                    "option1": variant.option1.item_name if variant.option1 else None,
                    "option2": variant.option2.item_name if variant.option2 else None,
                    "option3": variant.option3.item_name if variant.option3 else None,
                    "created_at": DateTime.string(variant.created_at),
                    "updated_at": DateTime.string(variant.updated_at),
                }
            )

        if product_variants:
            return product_variants
        return None
