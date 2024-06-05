from django.db import models


class Option(models.Model):
    option_name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.option_name


class OptionItem(models.Model):
    option = models.ForeignKey(Option, on_delete=models.CASCADE, related_name="items")
    item_name = models.CharField(max_length=255)

    class Meta:
        unique_together = ("option", "item_name")

    def __str__(self):
        return self.item_name
