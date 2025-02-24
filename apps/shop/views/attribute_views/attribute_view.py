from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets, status, serializers
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from apps.shop.models.attribute import Attribute, AttributeItem
from apps.shop.paginations import DefaultPagination
from apps.shop.serializers.attribute_serializers import (
    AttributeSerializer,
    AttributeItemSerializer,
)


@extend_schema_view(
    create=extend_schema(tags=["Attribute"], summary="Create a new attribute"),
    retrieve=extend_schema(tags=["Attribute"], summary="Retrieve a single attribute"),
    list=extend_schema(tags=["Attribute"], summary="Retrieve a list of attributes"),
    update=extend_schema(tags=["Attribute"], summary="Update an attribute"),
    destroy=extend_schema(tags=["Attribute"], summary="Deletes an attribute"),
)
class AttributeViewSet(viewsets.ModelViewSet):
    # TODO write test for check attributes is order by created-at
    queryset = Attribute.objects.all().order_by("-created_at")
    serializer_class = AttributeSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ["post", "get", "put", "delete"]
    # TODO add test for pagination
    ordering_fields = [
        "attribute_name",
    ]
    pagination_class = DefaultPagination

    ACTION_PERMISSIONS = {
        "list": [AllowAny()],
        "retrieve": [AllowAny()],
    }

    def get_permissions(self):
        return self.ACTION_PERMISSIONS.get(self.action, super().get_permissions())


@extend_schema_view(
    create=extend_schema(
        tags=["Attribute Item"], summary="Create a new attribute item"
    ),
    retrieve=extend_schema(
        tags=["Attribute Item"], summary="Retrieve a single attribute item"
    ),
    list=extend_schema(
        tags=["Attribute Item"], summary="Retrieve a list of attributes items"
    ),
    update=extend_schema(tags=["Attribute Item"], summary="Update an attribute item"),
    destroy=extend_schema(tags=["Attribute Item"], summary="Deletes an attribute item"),
)
class AttributeItemViewSet(viewsets.ModelViewSet):
    serializer_class = AttributeItemSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ["post", "get", "put", "delete"]

    ACTION_PERMISSIONS = {
        "list": [AllowAny()],
        "retrieve": [AllowAny()],
    }

    def get_queryset(self):
        attribute_id = self.kwargs.get("attribute_id")
        get_object_or_404(Attribute, pk=attribute_id)
        # TODO write test for check attribute items is order by created-at
        return AttributeItem.objects.filter(attribute_id=attribute_id).order_by(
            "-created_at"
        )

    def get_permissions(self):
        return self.ACTION_PERMISSIONS.get(self.action, super().get_permissions())

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        attribute_item = self.perform_create(serializer)
        serializer = self.serializer_class(attribute_item)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        attribute_id = self.kwargs.get("attribute_id")
        item_name = serializer.validated_data.get("item_name")
        get_object_or_404(Attribute, pk=attribute_id)
        try:
            item = AttributeItem.objects.create(
                attribute_id=attribute_id, item_name=item_name
            )
        except IntegrityError:
            raise serializers.ValidationError(
                {"detail": "This attribute item already exists."}
            )
        return item
