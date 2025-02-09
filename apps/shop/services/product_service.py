from itertools import product as options_combination

from django.db.models import Prefetch, Min, Max, Sum

from apps.shop.models.attribute import Attribute, AttributeItem
from apps.shop.models.product import (
    Product,
    ProductOption,
    ProductOptionItem,
    ProductVariant,
    ProductImage,
    ProductAttribute,
    ProductVariantImage,
)


class ProductService:
    product = None
    price: int | float
    stock: int
    sku: str
    options: list | None = []
    options_data: list = []
    attributes_data: list = []
    variants: list = []
    media: list | None = None

    @classmethod
    def create_product(cls, **data) -> Product:
        # Extract relevant data
        cls.price = data.pop("price", 0.00)
        cls.stock = data.pop("stock", 0)
        # TODO write tests for sku field on API endpoints
        cls.sku = data.pop("sku", "")
        cls.options_data = data.pop("options", [])
        cls.attributes_data = data.pop("attributes", [])

        cls.product = Product.objects.create(**data)
        cls.__manage_options()
        cls.__manage_attributes()

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
        cls.attributes_data = data.pop("attributes", [])

        # Update the product instance fields
        cls.product = product
        for attr, value in data.items():
            setattr(cls.product, attr, value)

        cls.product.save()
        cls.__manage_options()
        cls.__manage_attributes()

        # Return product object
        return cls.retrieve_product_details(product.id)

    @classmethod
    def __manage_options(cls):
        if cls.options_data:
            items_to_create = []
            options_to_retain = set()

            for data in cls.options_data:
                option_name = data["option_name"]
                option_items = data["items"]

                # Create or get a ProductOption instance for each option_name
                option_object, created = ProductOption.objects.get_or_create(
                    product=cls.product, option_name=option_name
                )

                options_to_retain.add(option_object.id)  # Retain this option

                if created:
                    # If the option is newly created, add all items
                    for item in option_items:
                        new_item = ProductOptionItem(
                            option=option_object, item_name=item
                        )
                        items_to_create.append(new_item)
                else:
                    # For existing options, update items
                    current_items = set(
                        option_object.items.values_list("item_name", flat=True)
                    )
                    new_items_set = set(option_items)
                    items_to_add = new_items_set - current_items
                    items_to_remove = current_items - new_items_set

                    # Add new items
                    for item in items_to_add:
                        new_item = ProductOptionItem(
                            option=option_object, item_name=item
                        )
                        items_to_create.append(new_item)

                    # Remove items that are no longer present
                    option_object.items.filter(item_name__in=items_to_remove).delete()

            # Bulk create the new product option-items
            ProductOptionItem.objects.bulk_create(items_to_create)

            # Remove options that are not in the current options_data
            ProductOption.objects.filter(product=cls.product).exclude(
                id__in=options_to_retain
            ).delete()

        else:
            cls.options = None
            ProductOption.objects.filter(product=cls.product).delete()

        cls.__manage_variants()

    @classmethod
    def __manage_variants(cls):
        # Fetch existing variants
        existing_variants = list(
            ProductVariant.objects.filter(product=cls.product).values(
                "id", "option1_id", "option2_id", "option3_id", "price", "stock", "sku"
            )
        )

        # Get the IDs of items related to product options
        items_id = cls.__get_item_ids_by_product_id(cls.product.id)
        new_variants_combinations = list(options_combination(*items_id))
        new_variants_to_create = []

        # Create a map of existing variants for easy lookup
        existing_variants_map = {
            (
                variant["option1_id"],
                variant["option2_id"],
                variant["option3_id"],
            ): variant
            for variant in existing_variants
        }

        # Track variants to retain
        variants_to_retain = set()

        # Iterate over the new combinations and handle update or create
        for variant in new_variants_combinations:
            values_tuple = tuple(variant)
            while len(values_tuple) < 3:
                values_tuple += (None,)
            option1, option2, option3 = values_tuple

            existing_variant = existing_variants_map.get((option1, option2, option3))

            if existing_variant:
                # Retain the variant if it matches the new combination
                variants_to_retain.add(existing_variant["id"])

                # Update the existing variant with the same options
                updated_variant = ProductVariant(
                    id=existing_variant["id"],  # Keep the same ID to update
                    product=cls.product,
                    option1_id=option1,
                    option2_id=option2,
                    option3_id=option3,
                    price=existing_variant[
                        "price"
                    ],  # Retain existing price, stock, and sku
                    stock=existing_variant["stock"],
                    sku=existing_variant["sku"],
                )
            else:
                # Create a new variant for the new combination
                updated_variant = ProductVariant(
                    product=cls.product,
                    option1_id=option1,
                    option2_id=option2,
                    option3_id=option3,
                    price=cls.price,  # Set new price, stock, and sku for new variants
                    stock=cls.stock,
                    sku=cls.sku,
                )

            new_variants_to_create.append(updated_variant)

        # Bulk create new and updated variants
        x = ProductVariant.objects.bulk_create(
            new_variants_to_create, ignore_conflicts=True
        )

        # Identify and delete old variants that are no longer valid
        variant_ids_to_delete = (
            set(variant["id"] for variant in existing_variants) - variants_to_retain
        )

        if variant_ids_to_delete:
            ProductVariant.objects.filter(id__in=variant_ids_to_delete).delete()

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
    def create_product_images(cls, product_id, **images_data) -> list[ProductImage]:
        is_main_flag = images_data.pop("is_main", False)

        images = [
            ProductImage.objects.create(
                product_id=product_id, src=image_data, is_main=is_main_flag and i == 0
            )
            for i, image_data in enumerate(images_data["images"])
        ]
        return images

    @classmethod
    def upload_product_images(cls, product_id, **images_data):
        cls.create_product_images(product_id, **images_data)

        # retrieve all images of current product
        return ProductImage.objects.filter(product_id=product_id)

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

    @classmethod
    def get_product_queryset(cls, request):
        # Annotate each product with minimum price, maximum price, and total stock from its variants.
        annotated_queryset = Product.objects.annotate(
            min_price=Min("variants__price"),
            max_price=Max("variants__price"),
            total_stock=Sum("variants__stock"),
        ).select_related(
            "category"
        )  # Optimize DB query by joining related category.

        # Prefetch product options along with their items.
        options_prefetch = Prefetch(
            "options",
            queryset=ProductOption.objects.prefetch_related("items"),
        )

        # Prefetch product variants with their options and images.
        variants_prefetch = Prefetch(
            "variants",
            queryset=ProductVariant.objects.select_related(
                "option1", "option2", "option3"
            )
            .prefetch_related(
                Prefetch(
                    "images",
                    queryset=ProductVariantImage.objects.select_related(
                        "product_image"
                    ),
                )
            )
            .order_by("id"),  # Order variants by their ID.
        )

        # Prefetch product attributes and their corresponding attribute details.
        attributes_prefetch = Prefetch(
            "productattribute_set",
            queryset=ProductAttribute.objects.select_related("attribute"),
        )

        # Combine all prefetches with the annotated queryset.
        queryset = annotated_queryset.prefetch_related(
            options_prefetch,
            variants_prefetch,
            "media",  # Prefetch product media (images).
            attributes_prefetch,
        )

        # For non-staff users, exclude products with a draft status.
        if not request.user.is_staff:
            queryset = queryset.exclude(status=Product.STATUS_DRAFT)

        # Return the final queryset ordered by creation date in descending order.
        return queryset.order_by("-created_at")

    @classmethod
    def __manage_attributes(cls):
        """
        Manage attributes for a product.

        This method handles the creation, update, and deletion of attributes for a product.
        It performs the following operations:
        1. If attributes are provided, it creates new attributes and associates them with the product.
        2. If no attributes are provided, it removes all existing attributes associated with the product.
        """
        # Clear existing attributes if no new attributes are provided
        if not cls.attributes_data:
            ProductAttribute.objects.filter(product=cls.product).delete()
            return

        # Extract attribute IDs and item IDs from the provided data
        attribute_ids = [attr_data["attribute_id"] for attr_data in cls.attributes_data]
        item_ids = {
            item_id
            for attr_data in cls.attributes_data
            for item_id in attr_data["items_id"]
        }

        # Fetch all attributes and items in bulk to minimize queries
        attributes = Attribute.objects.filter(id__in=attribute_ids).prefetch_related(
            "items"
        )
        items = AttributeItem.objects.filter(id__in=item_ids)

        # Prepare ProductAttribute instances
        product_attributes = []
        for attr_data in cls.attributes_data:
            attribute_id = attr_data["attribute_id"]
            attribute = next(
                (attr for attr in attributes if attr.id == attribute_id), None
            )

            if attribute:
                product_attribute = ProductAttribute(
                    product=cls.product, attribute=attribute
                )
                product_attributes.append(product_attribute)

        # Bulk create ProductAttributes and get the created instances
        created_product_attributes = ProductAttribute.objects.bulk_create(
            product_attributes
        )

        # Prepare M2M relationships for valid items
        m2m_entries = []
        for attr_data, product_attribute in zip(
            cls.attributes_data, created_product_attributes
        ):
            attribute_id = attr_data["attribute_id"]
            attribute = next(
                (attr for attr in attributes if attr.id == attribute_id), None
            )

            if attribute:
                valid_items = items.filter(attribute=attribute)
                m2m_entries.extend(
                    ProductAttribute.items.through(
                        productattribute_id=product_attribute.id,
                        attributeitem_id=item.id,
                    )
                    for item in valid_items
                )

        # Bulk create M2M relationships
        if m2m_entries:
            ProductAttribute.items.through.objects.bulk_create(m2m_entries)
