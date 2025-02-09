from typing import List, Any

from django.db.models import Prefetch, Min, Max, Sum

from apps.shop.models.product import (
    ProductOptionItem,
    ProductVariant,
    Product,
    ProductAttribute,
    ProductVariantImage,
    ProductOption,
)


class ProductRepository:
    @staticmethod
    def get_product_queryset(request):
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

    @staticmethod
    def get_item_ids_by_product_id(product_id: int) -> List[int]:
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
    def retrieve_product_details(cls, product_id: int) -> Any:
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
