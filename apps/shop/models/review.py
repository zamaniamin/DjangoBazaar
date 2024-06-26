from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Review(models.Model):
    message = models.TextField(
        help_text="Comment text",
        max_length=500,
    )
    product = models.ForeignKey(
        "Product",
        related_name="reviews",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    rating = models.FloatField(
        help_text="Rating of the product",
        null=True,
        blank=True,
    )
    user = models.ForeignKey(
        User, related_name="reviews", null=True, blank=True, on_delete=models.CASCADE
    )
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("accepted", "Accepted"),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")

    class Meta:
        ordering = ["rating"]

    def __str__(self):
        return f"Review by {self.user.email}"

    def __repr_self(self):
        return self.user.email
