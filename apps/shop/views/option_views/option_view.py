from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from apps.shop.models import Option, OptionItem
from apps.shop.paginations import DefaultPagination
from apps.shop.serializers import option_serializers
from apps.shop.serializers.option_serializers import OptionItemSerializer


@extend_schema_view(
    create=extend_schema(tags=["Option"], summary="Create a new option"),
    retrieve=extend_schema(tags=["Option"], summary="Retrieve a single option"),
    list=extend_schema(tags=["Option"], summary="Retrieve a list of options"),
    update=extend_schema(tags=["Option"], summary="Update an option"),
    partial_update=extend_schema(tags=["Option"], summary="Partial update an option"),
    destroy=extend_schema(tags=["Option"], summary="Deletes an option"),
)
class OptionViewSet(viewsets.ModelViewSet):
    queryset = Option.objects.all()
    serializer_class = option_serializers.OptionSerializer
    permission_classes = [IsAdminUser]
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


@extend_schema_view(
    create=extend_schema(tags=["Option Item"], summary="Create a new option item"),
    retrieve=extend_schema(
        tags=["Option Item"], summary="Retrieve a single option item"
    ),
    list=extend_schema(
        tags=["Option Item"], summary="Retrieve a list of options items"
    ),
    update=extend_schema(tags=["Option Item"], summary="Update an option item"),
    partial_update=extend_schema(
        tags=["Option Item"], summary="Partial update an option item"
    ),
    destroy=extend_schema(tags=["Option Item"], summary="Deletes an option item"),
)
class OptionItemViewSet(viewsets.ModelViewSet):
    queryset = OptionItem.objects.all()
    serializer_class = option_serializers.OptionItemSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ["post", "get", "put", "delete"]

    ACTION_PERMISSIONS = {
        "list": [AllowAny()],
        "retrieve": [AllowAny()],
    }

    def get_permissions(self):
        return self.ACTION_PERMISSIONS.get(self.action, super().get_permissions())

    def create(self, request, *args, **kwargs):
        # validate data
        option_id = kwargs["option_pk"]
        serializer = self.get_serializer(
            data=request.data, context={"option_pk": option_id}
        )
        serializer.is_valid(raise_exception=True)

        # check option is exist or not
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
                {"detail": "This option item already exist in items."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # return response
        response_serializer = OptionItemSerializer(option_item)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        get_object_or_404(Option, pk=self.kwargs["option_pk"])
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        get_object_or_404(Option, pk=self.kwargs["option_pk"])
        return super().destroy(request, *args, **kwargs)
