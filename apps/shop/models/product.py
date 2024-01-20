import os
import sys
import uuid

from django.db import models


# TODO add product manager
# class Product(models.Manager):
#     ...
class Product(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_ARCHIVED = "archived"
    STATUS_DRAFT = "draft"
    STATUS_CHOICES = [
        # The product is ready to sell and is available to customers on the online store, sales channels, and apps.
        (STATUS_ACTIVE, "Active"),
        # The product is no longer being sold and isn't available to customers on sales channels and apps.
        (STATUS_ARCHIVED, "Archived"),
        # The product isn't ready to sell and is unavailable to customers on sales channels and apps.
        (STATUS_DRAFT, "Draft"),
    ]

    product_name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=STATUS_DRAFT
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    published_at = models.DateTimeField(blank=True, null=True)

    # objects = models.Manager()

    def __str__(self):
        return self.product_name


class ProductOption(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="options"
    )
    option_name = models.CharField(max_length=255)

    class Meta:
        unique_together = ("product", "option_name")

    def __str__(self):
        return self.option_name


class ProductOptionItem(models.Model):
    option = models.ForeignKey(
        ProductOption, on_delete=models.CASCADE, related_name="items"
    )
    item_name = models.CharField(max_length=255)

    class Meta:
        unique_together = ("option", "item_name")

    def __str__(self):
        return self.item_name


class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="variants"
    )
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    stock = models.PositiveSmallIntegerField()

    option1 = models.ForeignKey(
        ProductOptionItem,
        related_name="option1",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    option2 = models.ForeignKey(
        ProductOptionItem,
        related_name="option2",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    option3 = models.ForeignKey(
        ProductOptionItem,
        related_name="option3",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


def generate_upload_path(instance, filename):
    unique_id = uuid.uuid4().hex
    _, ext = os.path.splitext(filename)

    # Add "test_" prefix to unique_id if running in test mode
    if "test" in sys.argv:
        unique_id = f"test_{unique_id}"
    return f"products/{instance.product.id}/{unique_id}{ext}"


class ProductMedia(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="media")
    src = models.ImageField(upload_to=generate_upload_path, blank=True, null=True)
    alt = models.CharField(max_length=250, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
