from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from apps.shop.models import Review
from apps.shop.paginations import DefaultPagination
from apps.shop.serializers import review_serializers


@extend_schema_view(
    create=extend_schema(tags=["Review"], summary="Create a new review"),
    retrieve=extend_schema(tags=["Review"], summary="Retrieve a single review"),
    list=extend_schema(tags=["Review"], summary="Retrieve a list of reviews"),
    update=extend_schema(tags=["Review"], summary="Update an review"),
    destroy=extend_schema(tags=["Review"], summary="Deletes an review"),
)
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = review_serializers.ReviewSerializer
    permission_classes = [IsAdminUser, IsAuthenticated]
    http_method_names = ["post", "get", "put", "delete"]
    # TODO add test for pagination
    ordering_fields = [
        "rating",
    ]
    pagination_class = DefaultPagination
    ACTION_PERMISSIONS = {
        "list": [AllowAny()],
        "retrieve": [AllowAny()],
    }

    def get_permissions(self):
        return self.ACTION_PERMISSIONS.get(self.action, super().get_permissions())

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @api_view(["POST"])
    def accept_review(request, review_id):
        try:
            review = Review.objects.get(pk=review_id)
            review.status = "accepted"
            review.save()
            return Response({"status": "Review accepted"})
        except Review.DoesNotExist:
            return Response({"error": "Review not found"}, status=404)

    @api_view(["POST"])
    def reject_review(request, review_id):
        try:
            review = Review.objects.get(pk=review_id)
            review.delete()
            return Response({"status": "Review rejected"})
        except Review.DoesNotExist:
            return Response({"error": "Review not found"}, status=404)
