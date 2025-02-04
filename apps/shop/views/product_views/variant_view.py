from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import mixins
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.shop.models.product import ProductVariant, ProductVariantImage
from apps.shop.serializers import product_serializers


@extend_schema_view(
    retrieve=extend_schema(
        tags=["Product Variant"], summary="Retrieves a single product variant"
    ),
    update=extend_schema(
        tags=["Product Variant"], summary="Updates an existing product variant"
    ),
    partial_update=extend_schema(
        tags=["Product Variant"], summary="Partial updates an existing product variant"
    ),
    destroy=extend_schema(
        tags=["Product Variant"], summary="Remove an existing product variant"
    ),
)
class VariantViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = ProductVariant.objects.all()
    serializer_class = product_serializers.ProductVariantSerializer
    permission_classes = [IsAdminUser]

    ACTION_PERMISSIONS = {"retrieve": [AllowAny()]}

    def get_permissions(self):
        return self.ACTION_PERMISSIONS.get(self.action, super().get_permissions())

    def update(self, request, *args, **kwargs):
        # Get the variant instance
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        # Update the variant using the serializer
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Process images_id
        images_id = request.data.get("images_id", [])
        if images_id:
            # Remove existing images not in the new list
            ProductVariantImage.objects.filter(variant=instance).exclude(
                product_image_id__in=images_id
            ).delete()

            # Add new images
            for image_id in images_id:
                ProductVariantImage.objects.get_or_create(
                    variant=instance, product_image_id=image_id
                )
        else:
            # Remove all existing images if no new images are provided
            # todo add tests too
            ProductVariantImage.objects.filter(variant=instance).delete()

        return Response(serializer.data)
