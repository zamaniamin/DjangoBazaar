from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny, IsAdminUser

from apps.shop.filters.option_filter import OptionFilter
from apps.shop.models import Option
from apps.shop.paginations import DefaultPagination
from apps.shop.serializers import option_serializers
from apps.shop.services.option_service import OptionService


@extend_schema_view(
    create=extend_schema(tags=["Option"], summary="Create a new option"),
    retrieve=extend_schema(tags=["Option"], summary="Retrieve a single option."),
    list=extend_schema(tags=["Option"], summary="Retrieve a list of options"),
    update=extend_schema(tags=["Option"], summary="Update a option"),
    partial_update=extend_schema(tags=["Option"], summary="Partial update a option"),
    destroy=extend_schema(tags=["Option"], summary="Deletes a option"),
)
class OptionViewSet(viewsets.ModelViewSet):
    queryset = Option.objects.all()
    serializer_class = option_serializers.OptionSerializer
    permission_classes = [IsAdminUser]
    # TODO add test case for search, filter, ordering and pagination
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ["option_name"]
    filterset_class = OptionFilter
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
    serializer_class = option_serializers.OptionItemSerializer
    permission_classes = [IsAdminUser]
    # TODO add test case for search, filter, ordering and pagination
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ["item_name"]
    filterset_class = OptionFilter
    ordering_fields = [
        "item_name",
    ]
    pagination_class = DefaultPagination

    ACTION_SERIALIZERS = {
        "create": option_serializers.OptionItemSerializer,
    }

    ACTION_PERMISSIONS = {
        "list": [AllowAny()],
        "retrieve": [AllowAny()],
    }

    def get_serializer_class(self):
        return self.ACTION_SERIALIZERS.get(self.action, self.serializer_class)

    def get_permissions(self):
        return self.ACTION_PERMISSIONS.get(self.action, super().get_permissions())

    def get_queryset(self):
        return OptionService.get_option_queryset(self.request)

    # def create(self, request, *args, **kwargs):
    #     # Validate
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     payload = serializer.validated_data
    #
    #     # Create option
    #     option = OptionService.create_option(**payload)
    #
    #     # Return the serialized response
    #     return Response(
    #         serializer.to_representation(option), status=status.HTTP_201_CREATED
    #     )
