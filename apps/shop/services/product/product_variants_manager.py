from itertools import product as options_combination
from typing import Any

from apps.shop.models.product import ProductVariant
from apps.shop.services.product.product_data import ProductData
from apps.shop.services.product.product_repository import ProductRepository


class ProductVariantMixin:
    @staticmethod
    def manage_variants(product_data: ProductData) -> None:
        """Implement the logic for managing variants."""

        # Fetch existing variants
        existing_variants = list(
            ProductVariant.objects.filter(product=product_data.product).values(
                "id", "option1_id", "option2_id", "option3_id", "price", "stock", "sku"
            )
        )

        # Get the IDs of items related to product options
        items_id = ProductRepository.get_item_ids_by_product_id(product_data.product.id)
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
                    product=product_data.product,
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
                    product=product_data.product,
                    option1_id=option1,
                    option2_id=option2,
                    option3_id=option3,
                    price=product_data.price,  # Set new price, stock, and sku for new variants
                    stock=product_data.stock,
                    sku=product_data.sku,
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

    def create_product_variants(self, product_info: Any) -> None:
        # Implement the logic for creating product variants.
        print("Creating product variants for:", product_info)
