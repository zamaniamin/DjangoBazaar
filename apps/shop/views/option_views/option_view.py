from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from apps.shop.models.option import Option, OptionItem
from apps.shop.paginations import DefaultPagination
from apps.shop.serializers import option_serializers
from apps.shop.serializers.option_serializers import OptionItemSerializer


@extend_schema_view(
    create=extend_schema(tags=["Option"], summary="Create a new option"),
    retrieve=extend_schema(tags=["Option"], summary="Retrieve a single option"),
    list=extend_schema(
        tags=["Option"],
        summary="Retrieve a list of options",
        parameters=[
            OpenApiParameter(
                name="option_name",
                description="Filter options by name",
                required=False,
                type=str,
            )
        ],
    ),
    update=extend_schema(tags=["Option"], summary="Update an option"),
    destroy=extend_schema(tags=["Option"], summary="Deletes an option"),
)
class OptionViewSet(viewsets.ModelViewSet):
    serializer_class = option_serializers.OptionSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ["post", "get", "put", "delete"]
    # TODO add test for pagination
    ordering_fields = [
        "option_name",
    ]
    pagination_class = DefaultPagination

    ACTION_PERMISSIONS = {
        "list": [AllowAny()],
        "retrieve": [AllowAny()],
    }

    def get_permissions(self):
        return self.ACTION_PERMISSIONS.get(self.action, super().get_permissions())

    def get_queryset(self):
        # TODO write test for check options is order by created-at
        queryset = Option.objects.all().order_by("-created_at")
        # TODO write test for get option by `option_name`
        option_name = self.request.query_params.get("option_name", None)
        if option_name:
            queryset = queryset.filter(option_name=option_name)
        return queryset


@extend_schema_view(
    create=extend_schema(tags=["Option Item"], summary="Create a new option item"),
    retrieve=extend_schema(
        tags=["Option Item"], summary="Retrieve a single option item"
    ),
    list=extend_schema(
        tags=["Option Item"], summary="Retrieve a list of options items"
    ),
    update=extend_schema(tags=["Option Item"], summary="Update an option item"),
    destroy=extend_schema(tags=["Option Item"], summary="Deletes an option item"),
)
class OptionItemViewSet(viewsets.ModelViewSet):
    serializer_class = option_serializers.OptionItemSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ["post", "get", "put", "delete"]

    ACTION_PERMISSIONS = {
        "list": [AllowAny()],
        "retrieve": [AllowAny()],
    }

    def get_queryset(self):
        option_id = self.kwargs.get("option_id")
        get_object_or_404(Option, pk=option_id)
        # TODO write test for check option items is order by created-at
        return OptionItem.objects.filter(option_id=option_id).order_by("-created_at")

    def get_permissions(self):
        return self.ACTION_PERMISSIONS.get(self.action, super().get_permissions())

    def create(self, request, *args, **kwargs):
        # validate data
        option_id = self.kwargs.get("option_id")
        serializer = self.get_serializer(
            data=request.data, context={"option_id": option_id}
        )
        serializer.is_valid(raise_exception=True)

        # check option is exist or not
        # TODO can I remove this line?
        get_object_or_404(Option, pk=option_id)

        # get validated data
        payload = serializer.validated_data
        item_name = payload["item_name"]

        try:
            option_item = OptionItem.objects.create(
                option_id=option_id, item_name=item_name
            )
        except IntegrityError:
            return Response(
                {"item_name": "item with this item name already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # return response
        response_serializer = OptionItemSerializer(option_item)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
