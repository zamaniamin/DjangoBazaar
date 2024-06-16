from faker import Faker

from apps.shop.models.category import Category


class CategoryFactory:
    faker = Faker()
    sample_name = "sample category"

    @classmethod
    def create_category(cls, name=""):
        if name:
            return Category.objects.create(name=name)
        return Category.objects.create(name=cls.sample_name)
