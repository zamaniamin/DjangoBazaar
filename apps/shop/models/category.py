from django.db import models
from django.utils.text import slugify

from apps.core.models.image import AbstractImage
from apps.core.models.timestamped import TimestampedModel


class Category(TimestampedModel):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, allow_unicode=True)
    description = models.TextField(null=True, blank=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",  # Add a reverse relation to easily access children
    )

    def get_parents_hierarchy(self):
        hierarchy = []
        category = self
        while category.parent is not None:
            hierarchy.append(
                {
                    "id": category.parent.id,
                    "name": category.parent.name,
                }
            )
            category = category.parent
        return hierarchy[::-1]  # Reverse the list to get the highest ancestor first

    def get_children_hierarchy(self):
        def fetch_children(category):
            children = []
            for child in category.children.all():
                children.append(
                    {
                        "id": child.id,
                        "name": child.name,
                        "children": fetch_children(
                            child
                        ),  # Recursively get child hierarchy
                    }
                )
            return children

        return fetch_children(self)

    def automatic_slug_creation(self):
        # TODO fix bug on automatic assign count
        if not self.slug:
            base_slug = slugify(self.name, allow_unicode=True)
            slug = base_slug
            count = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1
            self.slug = slug

    def save(self, *args, **kwargs):
        self.automatic_slug_creation()
        super().save(*args, **kwargs)


class CategoryImage(AbstractImage):
    category = models.OneToOneField(
        Category, on_delete=models.CASCADE, related_name="image"
    )

    def get_related_id(self):
        return self.category.id

    def get_related_folder(self):
        return "categories"
