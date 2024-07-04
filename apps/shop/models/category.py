import os
import sys
import uuid

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
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
