from apps.shop.models.product import ProductImage


class ProductImageMixin:
    @staticmethod
    def create_product_images(product_id, **images_data) -> list[ProductImage]:
        is_main_flag = images_data.pop("is_main", False)

        images = [
            ProductImage.objects.create(
                product_id=product_id, src=image_data, is_main=is_main_flag and i == 0
            )
            for i, image_data in enumerate(images_data["images"])
        ]
        return images

    @classmethod
    def upload_product_images(cls, product_id: int, **images):
        cls.create_product_images(product_id, **images)

        # retrieve all images of current product
        return ProductImage.objects.filter(product_id=product_id)
