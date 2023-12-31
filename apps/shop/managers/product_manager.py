from django.db.models import Manager


class ProductManager(Manager):
    product = None
    price: int | float
    stock: int
    options: list | None = []
    options_data: list = []
    variants: list = []
    media: list | None = None

    def create_product(self, **data):
        try:
            self.price = data.pop('price', 0)
            self.stock = data.pop('stock', 0)
            self.options_data = data.pop('options')
        except KeyError:
            ...

        # --- create product ---
        self.product = self.model.objects.create(**data)

        # --- create options ---
        self.__create_product_options()

        return self.product, self.options

    def __create_product_options(self):
        """
        Create new option if it doesn't exist and update its items.
        """
        from apps.shop.models.product import ProductOption, ProductOptionItem

        if self.options_data:
            for option in self.options_data:
                new_option = ProductOption.objects.create(product=self.product, option_name=option['option_name'])

                for item in option['items']:
                    ProductOptionItem.objects.create(option=new_option, item_name=item)
            self.options = self.retrieve_options(self.product.id)
        else:
            self.options = None

    @staticmethod
    def retrieve_options(product_id):
        """
        Get all options of a product
        """
        from apps.shop.models.product import ProductOption, ProductOptionItem

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
