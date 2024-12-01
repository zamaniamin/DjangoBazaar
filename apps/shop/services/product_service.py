from itertools import product as options_combination

from django.db.models import Prefetch

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
    sku: str
    options: list | None = []
    options_data: list = []
    variants: list = []
    media: list | None = None

    @classmethod
    def create_product(cls, **data) -> Product:
        # Extract relevant data
        cls.price = data.pop("price")
        cls.stock = data.pop("stock")
        # TODO write tests for sku field on API endpoints
        cls.sku = data.pop("sku")
        cls.options_data = data.pop("options")

        # Create product
        cls.product = Product.objects.create(**data)

        # Create options
        cls.__manage_options()

        # Return product object
        return cls.retrieve_product_details(cls.product.id)

    @classmethod
    def update_product(cls, product: Product, **data) -> Product:
        # Extract relevant data
        cls.price = data.pop("price", 0.00)
        cls.stock = data.pop("stock", 0)
        # TODO write tests for sku field on API endpoints
        cls.sku = data.pop("sku", "")
        cls.options_data = data.pop("options", [])

        # Update the product instance fields
        cls.product = product
        for attr, value in data.items():
            setattr(cls.product, attr, value)

        # Save the updated product
        cls.product.save()

        # create or update options
        cls.__manage_options()

        # Return product object
        return cls.retrieve_product_details(product.id)

    @classmethod
    def __manage_options(cls):
        # todo update variants.
        if cls.options_data:
            items_to_create = []

            for data in cls.options_data:
                option_name = data["option_name"]
                option_items = data["items"]

                # Create a ProductOption instance for each option_name
                option_object, created = ProductOption.objects.get_or_create(
                    product=cls.product, option_name=option_name
                )

                if created:
                    for item in option_items:
                        # Create a ProductOptionItem instance for each item
                        new_item = ProductOptionItem(
                            option=option_object, item_name=item
                        )
                        items_to_create.append(new_item)

                else:
                    current_items = set(
                        option_object.items.values_list("item_name", flat=True)
                    )
                    new_items_set = set(option_items)
                    items_to_add = new_items_set - current_items
                    items_to_remove = current_items - new_items_set

                    for item in items_to_add:
                        # Create a ProductOptionItem instance for each item
                        new_item = ProductOptionItem(
                            option=option_object, item_name=item
                        )
                        items_to_create.append(new_item)

                    # Remove items no longer present
                    option_object.items.filter(item_name__in=items_to_remove).delete()

            # Bulk create the product option-items
            ProductOptionItem.objects.bulk_create(items_to_create)

            # generate and create product variants
            cls.__create_product_variants(bulk_create=True)
        else:
            # If no options_data is provided, set cls.options to None
            cls.__create_product_variants()
            cls.options = None

    @classmethod
    def __manage_variants(cls):
        ...

    @classmethod
    def create_product_images(cls, product_id, **images_data):
        images = [
            ProductMedia(product_id=product_id, src=image_data)
            for image_data in images_data["images"]
        ]
        return ProductMedia.objects.bulk_create(images)

    @classmethod
    def upload_product_images(cls, product_id, **images_data):
        cls.create_product_images(product_id, **images_data)

        # retrieve all images of current product
        return ProductMedia.objects.filter(product_id=product_id)

    @staticmethod
    def retrieve_product_details(product_id):
        """
        Retrieve and return product details with optimized queries.

        Args:
            product_id (int): The ID of the product to retrieve.

        Returns:
            Product: The product object with related options and variants ad media.

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
                    sku=cls.sku,
                )
                variants_to_create.append(new_variant)

            # Bulk create the variants in the database
            ProductVariant.objects.bulk_create(variants_to_create)
        else:
            # Create a single ProductVariant instance for the product
            ProductVariant.objects.create(
                product=cls.product, price=cls.price, stock=cls.stock, sku=cls.sku
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

    @classmethod
    def get_product_queryset(cls, request):
        queryset = Product.objects.select_related().prefetch_related(
            "options__items",
            Prefetch(
                "variants",
                queryset=ProductVariant.objects.select_related(
                    "option1", "option2", "option3"
                ).order_by("id"),
            ),
            "media",
        )

        if not request.user.is_staff:
            queryset = queryset.exclude(status=Product.STATUS_DRAFT)

        return queryset.order_by("-created_at")
