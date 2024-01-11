from django.db.models import Prefetch
from rest_framework import viewsets, status
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response

from apps.shop.models import Product, ProductVariant
from apps.shop.serializers import product_serializers as s
from apps.shop.services.product_service import ProductService


class ProductView(viewsets.ModelViewSet):
    """
    A ViewSet for managing Product instances.

    Attributes:
        queryset: The queryset of Product instances.
        serializer_class: The serializer class for Product instances.
        permission_classes: The permission classes for accessing Product instances.

    ACTION_SERIALIZERS (dict): A dictionary mapping actions to specific serializer classes.
    ACTION_PERMISSIONS (dict): A dictionary mapping actions to specific permission classes.

    Methods:
        get_serializer_class(): Get the serializer class based on the current action.
        get_permissions(): Get the permissions based on the current action.

    """

    queryset = Product.objects.all()
    serializer_class = s.ProductSerializer
    permission_classes = [IsAdminUser]

    ACTION_SERIALIZERS = {
        "create": s.ProductCreateSerializer,
    }

    ACTION_PERMISSIONS = {"list": [AllowAny()], "retrieve": [AllowAny()]}

    def get_serializer_class(self):
        """
        Get the serializer class based on the current action.

        Returns:
            type: The serializer class to use for the current action.

        """
        return self.ACTION_SERIALIZERS.get(self.action, self.serializer_class)

    def get_permissions(self):
        """
        Get the permissions based on the current action.

        Returns:
            list: The list of permission classes to apply for the current action.

        """
        return self.ACTION_PERMISSIONS.get(self.action, super().get_permissions())

    def get_queryset(self):
        """
        Get the queryset for the Product model with related options and variants.

        Returns:
            QuerySet: A queryset for the Product model with select and prefetch related options and variants.

        Notes:
            - For non-admin users, products with a status of 'draft' are excluded from the queryset.

        """
        queryset = Product.objects.select_related().prefetch_related(
            "productoption_set__productoptionitem_set",
            Prefetch(
                "productvariant_set",
                queryset=ProductVariant.objects.select_related(
                    "option1", "option2", "option3"
                ),
            ),
        )

        user = self.request.user
        if not user.is_staff:  # Check if the user is not an admin
            queryset = queryset.exclude(status="draft")

        return queryset

    def create(self, request, *args, **kwargs):
        """
        Create method for product creation.

        This method is part of a view or API endpoint for creating a new product. It performs the following steps:

        1. Validates the request data using the provided serializer.
        2. Creates a product using the ProductService.create_product method with the validated data.
        3. Serializes the created product using the ProductSerializer.
        4. Returns the serialized response with HTTP 201 Created status.

        Parameters:
            - request: The HTTP request object.
            - args: Additional positional arguments.
            - kwargs: Additional keyword arguments.

        Returns:
            - Response: Serialized data of the created product with HTTP 201 Created status.
        """

        # Validate
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data

        # Create product
        product = ProductService.create_product(**payload)

        # Serialize the created product for the response
        response_serializer = s.ProductSerializer(product)

        # Return the serialized response
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
