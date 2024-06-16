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

    @classmethod
    def create_categories_list(cls):
        return (
            Category.objects.create(name=f"{cls.sample_name} 1"),
            Category.objects.create(name=f"{cls.sample_name} 2"),
        )
