from apps.shop.models.product import ProductOption, ProductOptionItem
from apps.shop.services.product.product_data import ProductData


class ProductOptionMixin:
    @staticmethod
    def manage_options(product_data: ProductData) -> None:
        """Implement the logic for handling options."""
        if product_data.options:
            items_to_create = []
            options_to_retain = set()

            for data in product_data.options:
                option_name = data["option_name"]
                option_items = data["items"]

                # Create or get a ProductOption instance for each option_name
                option_object, created = ProductOption.objects.get_or_create(
                    product=product_data.product, option_name=option_name
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
            ProductOption.objects.filter(product=product_data.product).exclude(
                id__in=options_to_retain
            ).delete()

        else:
            ProductOption.objects.filter(product=product_data.product).delete()
