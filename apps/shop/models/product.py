from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from apps.core.models.image import AbstractImage


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
    # TODO write test to check product accept unicode in the slug.
    # TODO auto add hyphens for space characters.
    slug = models.SlugField(
        max_length=255, unique=True, blank=True, null=True, allow_unicode=True
    )
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

    def save(self, *args, **kwargs):
        if self.product.options.count() >= 3:
            raise ValidationError(
                "You cannot add more than 3 options for this product.",
                code="max_options_exceeded",
            )
        super().save(*args, **kwargs)


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


class ProductImage(AbstractImage):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="media")
    is_main = models.BooleanField(default=False)

    def get_related_id(self):
        return self.product.id

    def get_related_folder(self):
        return "products"

    def save(self, *args, **kwargs):
        if self.is_main:
            # Unset previous main images for the product
            ProductImage.objects.filter(product=self.product, is_main=True).update(
                is_main=False
            )
        super(ProductImage, self).save(*args, **kwargs)


# class ProductVariantImage(AbstractImage):
#     variant = models.ForeignKey(
#         ProductVariant, on_delete=models.CASCADE, related_name="images"
#     )
#
#     def get_related_id(self):
#         return self.variant.id
#
#     def get_related_folder(self):
#         return "variants"

# TODO use `ProductVariantImage` instead of color image or color code, use variant image for color show
# todo add product options api
# todo add product categorize api
# todo add product features api
