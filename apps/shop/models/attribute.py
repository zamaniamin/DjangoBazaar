from django.db import models


class Attribute(models.Model):
    attribute_name = models.CharField(max_length=100, unique=True)

    # TODO write test for new fields `created_at` and `updated_at`
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["attribute_name"]

    def __str__(self):
        return self.attribute_name


class AttributeItem(models.Model):
    attribute = models.ForeignKey(
        Attribute, on_delete=models.CASCADE, related_name="items"
    )
    item_name = models.CharField(max_length=255)

    # TODO write test for new fields `created_at` and `updated_at`
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("attribute", "item_name")

    def __str__(self):
        return self.item_name
