from django.db import models


class Attribute(models.Model):
    class Meta:
        ordering = ["name"]

    name = models.CharField(
        verbose_name="Name",
        max_length=100,
        help_text="User attribute name",
    )

    def __str__(self):
        return self.name


class AttributeItem(models.Model):
    attribute = models.ForeignKey(
        Attribute, on_delete=models.CASCADE, related_name="items"
    )
    name = models.CharField(max_length=255)

    class Meta:
        unique_together = ("attribute", "name")

    def __str__(self):
        return self.name
