# python
from apps.shop.models.attribute import Attribute, AttributeItem
from apps.shop.models.product import ProductAttribute
from apps.shop.services.product.product_data import ProductData


class ProductAttributeMixin:
    @staticmethod
    def manage_attributes(product_data: ProductData) -> None:
        """
        Manage attributes for a product.

        This method handles the creation, update, and deletion of attributes for a product.
        It performs the following operations:
        1. If no attributes are provided, it removes all existing attributes associated with the product.
        2. Otherwise, it clears the current attributes and creates new ones based on the provided data.
        """
        # Remove all current attributes if no new attributes are provided
        if not product_data.attributes:
            ProductAttribute.objects.filter(product=product_data.product).delete()
            return

        # Delete existing product attributes to prevent duplicate entries
        ProductAttribute.objects.filter(product=product_data.product).delete()

        # Extract attribute IDs and item IDs from the provided data
        attribute_ids = [
            attr_data["attribute_id"] for attr_data in product_data.attributes
        ]
        item_ids = {
            item_id
            for attr_data in product_data.attributes
            for item_id in attr_data["items_id"]
        }

        # Fetch all attributes and items in bulk to minimize queries
        attributes = Attribute.objects.filter(id__in=attribute_ids).prefetch_related(
            "items"
        )
        items = AttributeItem.objects.filter(id__in=item_ids)

        # Prepare ProductAttribute instances
        product_attributes = []
        for attr_data in product_data.attributes:
            attribute_id = attr_data["attribute_id"]
            attribute = next(
                (attr for attr in attributes if attr.id == attribute_id), None
            )
            if attribute:
                product_attribute = ProductAttribute(
                    product=product_data.product, attribute=attribute
                )
                product_attributes.append(product_attribute)

        # Bulk create ProductAttributes and retrieve the created instances
        created_product_attributes = ProductAttribute.objects.bulk_create(
            product_attributes
        )

        # Prepare many-to-many relationships for valid items
        m2m_entries = []
        for attr_data, product_attribute in zip(
            product_data.attributes, created_product_attributes
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

        # Bulk create many-to-many relationships if any entries exist
        if m2m_entries:
            ProductAttribute.items.through.objects.bulk_create(m2m_entries)
