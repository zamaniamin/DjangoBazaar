from itertools import product as options_combination

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
        try:
            cls.price = data.pop('price', 0)
            cls.stock = data.pop('stock', 0)
            cls.options_data = data.pop('options')
        except KeyError:
            ...

        # --- create product ---
        cls.product = Product.objects.create(**data)

        # --- create options ---
        cls.__create_product_options()

        # --- create variants ---
        cls.__create_product_variants()

        return cls.product, cls.options, cls.variants

    @classmethod
    def __create_product_options(cls):
        """
        Create new option if it doesn't exist and update its items.
        """

        if cls.options_data:
            for option in cls.options_data:
                new_option = ProductOption.objects.create(product=cls.product, option_name=option['option_name'])

                for item in option['items']:
                    ProductOptionItem.objects.create(option=new_option, item_name=item)
            cls.options = cls.retrieve_options(cls.product.id)
        else:
            cls.options = None

    @classmethod
    def __create_product_variants(cls):
        """
        Create a default variant or create variants by options combination.
        """

        if cls.options:

            # create variants by options combination
            items_id = cls.__get_item_ids_by_product_id(cls.product.id)
            variants = list(options_combination(*items_id))
            for variant in variants:
                values_tuple = tuple(variant)

                # set each value to an option and set none if it doesn't exist
                while len(values_tuple) < 3:
                    values_tuple += (None,)
                option1, option2, option3 = values_tuple

                ProductVariant.objects.create(
                    product=cls.product,
                    option1=ProductOptionItem.objects.get(id=option1) if option1 else None,
                    option2=ProductOptionItem.objects.get(id=option2) if option2 else None,
                    option3=ProductOptionItem.objects.get(id=option3) if option3 else None,
                    price=cls.price,
                    stock=cls.stock
                )
        else:
            # set a default variant
            ProductVariant.objects.create(
                product_id=cls.product.id,
                price=cls.price,
                stock=cls.stock
            )

        cls.variants = cls.retrieve_variants(cls.product.id)

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

        product_options = []
        options = ProductOption.objects.filter(product=product_id)
        for option in options:
            items = ProductOptionItem.objects.filter(option=option)
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

        product_variants = []
        variants: list[ProductVariant] = ProductVariant.objects.filter(product=product_id)
        for variant in variants:
            product_variants.append({
                "variant_id": variant.id,
                "product_id": variant.product_id,
                "price": variant.price,
                "stock": variant.stock,
                "option1": ProductOptionItem.objects.get(
                    id=variant.option1.id).item_name if variant.option1 else None,
                "option2": ProductOptionItem.objects.get(
                    id=variant.option2.id).item_name if variant.option2 else None,
                "option3": ProductOptionItem.objects.get(
                    id=variant.option3.id).item_name if variant.option3 else None,
                "created_at": DateTime.string(variant.created_at),
                "updated_at": DateTime.string(variant.updated_at)
            })

        if product_variants:
            return product_variants
        return None
