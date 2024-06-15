import os
import sys
import uuid

from django.core.exceptions import ValidationError
from django.db import models


def generate_upload_path(instance, filename):
    unique_id = uuid.uuid4().hex
    _, ext = os.path.splitext(filename)

    # Add "test_" prefix to unique_id if running in test mode
    if "test" in sys.argv:
        return f"test/categories/{instance.id}/{unique_id}{ext}"
    else:
        return f"categories/{instance.id}/{unique_id}{ext}"


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    src = models.ImageField(upload_to=generate_upload_path, blank=True, null=True)
    subcategory_of = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subcategories",
    )

    def clean(self):
        if self.subcategory_of and self.subcategory_of == self:
            raise ValidationError("A category cannot be a subcategory of itself.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


# TODO subcategory_of cant be same as current category id
