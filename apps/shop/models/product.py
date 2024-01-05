from django.core.validators import MinValueValidator
from django.db import models


class Product(models.Model):
    """
    Represents a product in an online store.

    Attributes:
        product_name: The name of the product (required, max length 255).
        description: A description of the product (optional, can be null or empty).
        status: The status of the product (required, one of 'active', 'archived', or 'draft').
        created_at: The timestamp when the product was created (automatically set when the object is created).
        updated_at: The timestamp when the product was last updated (can be null if the product has not been updated).
        published_at: The timestamp when the product was published (optional, can be null if the product is not published).
    """
    product_name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    STATUS_CHOICES = [

        # The product is ready to sell and is available to customers on the online store, sales channels, and apps.
        ('active', 'Active'),

        # The product is no longer being sold and isn't available to customers on sales channels and apps.
        ('archived', 'Archived'),

        # The product isn't ready to sell and is unavailable to customers on sales channels and apps.
        ('draft', 'Draft'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    published_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.product_name


class ProductOption(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    option_name = models.CharField(max_length=255)

    class Meta:
        unique_together = ('product', 'option_name')

    def __str__(self):
        return self.option_name


class ProductOptionItem(models.Model):
    option = models.ForeignKey(ProductOption, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=255)

    class Meta:
        unique_together = ('option', 'item_name')

    def __str__(self):
        return self.item_name


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    option1 = models.ForeignKey(
        ProductOptionItem, related_name='option1', on_delete=models.CASCADE, null=True, blank=True)

    option2 = models.ForeignKey(
        ProductOptionItem, related_name='option2', on_delete=models.CASCADE, null=True, blank=True)

    option3 = models.ForeignKey(
        ProductOptionItem, related_name='option3', on_delete=models.CASCADE, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
