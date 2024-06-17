from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from apps.shop.models import Attribute, AttributeItem
from apps.shop.paginations import DefaultPagination
from apps.shop.serializers import attribute_serializers


@extend_schema_view(
    create=extend_schema(tags=["Attribute"], summary="Create a new attribute"),
    retrieve=extend_schema(tags=["Attribute"], summary="Retrieve a single attribute"),
    list=extend_schema(tags=["Attribute"], summary="Retrieve a list of attributes"),
    update=extend_schema(tags=["Attribute"], summary="Update an attribute"),
    destroy=extend_schema(tags=["Attribute"], summary="Deletes an attribute"),
)
class AttributeViewSet(viewsets.ModelViewSet):
    queryset = Attribute.objects.all()
    serializer_class = attribute_serializers.AttributeSerializer
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
    serializer_class = attribute_serializers.AttributeItemSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ["post", "get", "put", "delete"]

    ACTION_PERMISSIONS = {
        "list": [AllowAny()],
        "retrieve": [AllowAny()],
    }

    def get_queryset(self):
        attribute_id = self.kwargs.get("attribute_pk")
        get_object_or_404(Attribute, pk=attribute_id)
        return AttributeItem.objects.filter(attribute_id=attribute_id)

    def get_permissions(self):
        return self.ACTION_PERMISSIONS.get(self.action, super().get_permissions())

    def create(self, request, *args, **kwargs):
        # validate data
        attribute_id = kwargs["attribute_pk"]
        serializer = self.get_serializer(
            data=request.data, context={"attribute_pk": attribute_id}
        )
        serializer.is_valid(raise_exception=True)

        # check attribute is exist or not
        # TODO can I remove this line?
        get_object_or_404(Attribute, pk=attribute_id)

        # get validated data
        payload = serializer.validated_data
        name = payload["name"]

        try:
            attribute_item = AttributeItem.objects.create(
                attribute_id=attribute_id, name=name
            )
        except IntegrityError:
            return Response(
                {"detail": "This attribute item already exist in items."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # return response
        response_serializer = attribute_serializers.AttributeItemSerializer(
            attribute_item
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
