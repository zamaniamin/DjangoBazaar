from django.db import models

from apps.core.models.mixin import ModelMixin
from config import settings


# TODO create customer model
# TODO add user to customers when a cart is accepted


class OrderStatus(models.TextChoices):
    OPEN = "open", "Open"
    INVOICE_SENT = "invoice_sent", "Invoice Sent"
    COMPLETED = "completed", "Completed"


class FinancialStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PAID = "paid", "Paid"
    REFUNDED = "refunded", "Refunded"
    VOIDED = "voided", "Voided"


class OrderAddress(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    company = models.CharField(max_length=255, blank=True, null=True)
    phone = models.EmailField()
    country = models.CharField(max_length=255)
    province = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    zip = models.CharField(max_length=20)
    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)


class Order(ModelMixin):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    order_number = models.AutoField(unique=True, default=1001)
    ORDER_STATUS_open = "open"
    ORDER_STATUS_INVOICE_SENT = "invoice_sent"
    ORDER_STATUS_completed = "completed"

    order_status = models.CharField(
        max_length=12, default=ORDER_STATUS_open, choices=OrderStatus.choices
    )
    financial_status = models.CharField(
        max_length=10, default=FinancialStatus.PENDING, choices=FinancialStatus.choices
    )
    purchase_number = models.IntegerField(unique=True, blank=True, null=True)
    gateway = models.TextField()

    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_discounts = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_line_items_price = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00
    )
    taxes_included = models.BooleanField(default=False)
    total_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    shipping_address = models.OneToOneField(
        OrderAddress, related_name="shipping_address", on_delete=models.CASCADE
    )
    billing_address = models.OneToOneField(
        OrderAddress, related_name="billing_address", on_delete=models.CASCADE
    )

    note = models.TextField(blank=True)

    completed_at = models.DateTimeField(blank=True, null=True)


class OrderItem(ModelMixin):
    pass
    # custom
    # variant_id
    # product_id
    # name
    # quantity
    # gift_card
    # applied_discount
    # price
    # grams

    # variant price
