from rest_framework import serializers

from apps.shop.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["id", "user", "rating", "message", "status", "product"]
        read_only_fields = ["status", "user"]
