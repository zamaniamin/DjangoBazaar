import os
import sys
import uuid

from django.db import models
from django.utils import timezone
from django.utils.text import slugify


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

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=STATUS_DRAFT
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    published_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.status == Product.STATUS_ACTIVE:
            self.published_at = timezone.now()

        if not self.slug:
            # TODO add tests for slug on create, read, update
            base_slug = slugify(self.name, allow_unicode=True)
            slug = base_slug
            count = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1
            self.slug = slug

        super().save(*args, **kwargs)


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
    sku = models.CharField(max_length=100, blank=True, null=True)

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
    # TODO add slug field


def generate_upload_path(instance, filename):
    unique_id = uuid.uuid4().hex
    _, ext = os.path.splitext(filename)

    # Add "test_" prefix to unique_id if running in test mode
    if "test" in sys.argv:
        return f"test/products/{instance.product.id}/{unique_id}{ext}"
    else:
        return f"products/{instance.product.id}/{unique_id}{ext}"


class ProductMedia(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="media")
    src = models.ImageField(upload_to=generate_upload_path, blank=True, null=True)
    alt = models.CharField(max_length=250, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# todo add product options api
# todo add product colors api (under options menu, add meta fields 'meta_key=color_code' and 'meta_value=#ffffff')
# todo add product categorize api
# todo add product features api
