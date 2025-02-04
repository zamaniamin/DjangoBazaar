from django.db import models

from apps.core.models.timestamped import TimestampedModel


class Attribute(TimestampedModel):
    attribute_name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["attribute_name"]

    def __str__(self):
        return self.attribute_name


class AttributeItem(TimestampedModel):
    attribute = models.ForeignKey(
        Attribute, on_delete=models.CASCADE, related_name="items"
    )
    item_name = models.CharField(max_length=255)

    class Meta:
        unique_together = ("attribute", "item_name")

    def __str__(self):
        return self.item_name
