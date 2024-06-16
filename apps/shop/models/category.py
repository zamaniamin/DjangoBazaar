import os
import sys
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify


def generate_upload_path(instance, filename):
    # TODO remove privacy data from image files and only accept jpeg and png formats?
    unique_id = uuid.uuid4().hex
    _, ext = os.path.splitext(filename)

    # Add "test_" prefix to unique_id if running in test mode
    if "test" in sys.argv:
        return f"test/categories/{unique_id}{ext}"
    else:
        return f"categories/{unique_id}{ext}"


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to=generate_upload_path, blank=True, null=True)
    subcategory_of = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subcategories",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.subcategory_of and self.subcategory_of == self:
            raise ValidationError("A category cannot be a subcategory of itself.")

    def save(self, *args, **kwargs):
        self.clean()

        # TODO move this logic to a method `automatic_slug_creation()`
        if not self.slug:
            # TODO add tests for slug on create, read, update
            base_slug = slugify(self.name, allow_unicode=True)
            slug = base_slug
            count = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1
            self.slug = slug

        super().save(*args, **kwargs)


# TODO subcategory_of cant be same as current category id
