from django.db.models import Prefetch

from apps.shop.models.option import (
    Option,
    OptionItem,
)


class OptionService:
    option = None
    options: list | None = []
    options_data: list = []

    @classmethod
    def create_option(cls, **data):
        """
        Create a new option and return the option object.

        Note:
            This method creates a new option instance, generates options, and optimizes queries
            for retrieving the option with related options.

        """

        # Extract relevant data
        cls.options_data = data.pop("options")

        # Create Option
        cls.option = Option.objects.create(**data)

        # Create options
        cls.__create_option_options()

        # Return option object
        return cls.retrieve_option_details(cls.option.id)

    
    @classmethod
    def __create_option_options(cls):
        """
        Create options and associated items.

        Explanation:
        If cls.options_data is provided, it creates Option and OptionOptionItem instances
        based on the data provided. 

        """
        if cls.options_data:
            options_to_create = []
            items_to_create = []

            for option in cls.options_data:
                # Create an Option instance for each option_name
                new_option = Option(
                    option=cls.option, option_name=option["option_name"]
                )
                options_to_create.append(new_option)

                for item in option["items"]:
                    # Create a OptionItem instance for each item
                    new_item = OptionItem(option=new_option, item_name=item)
                    items_to_create.append(new_item)

            # Bulk create the options and items in the database
            Option.objects.bulk_create(options_to_create)
            OptionItem.objects.bulk_create(items_to_create)

        else:
            # If no options_data is provided, set cls.options to None
            cls.options = None

    @staticmethod
    def __get_item_ids_by_option_id(option_id):
        """
        Get item_ids grouped by option_id for a given option_id.

        Explanation: This method queries the ProductOptionItem table to retrieve item_ids associated with a given
        option_id. It groups the item_ids by option_id and returns a list of lists where each sublist contains
        item_ids for a specific option.

        Args:
        - option_id (int): The ID of the product for which to retrieve item_ids.

        Returns:
        List[List[int]]: A list of lists where each sublist contains item_ids for a specific option.

        """
        item_ids_by_option = []

        # Query the OptionItem table to retrieve item_ids
        items = OptionItem.objects.filter(
            option_id=option_id
        ).values_list("option_id", "id")

        # Group item_ids by option_id
        item_ids_dict = {}
        for option_id, item_id in items:
            item_ids_dict.setdefault(option_id, []).append(item_id)

        # Append `item_ids` lists to the result list
        item_ids_by_option.extend(item_ids_dict.values())

        return item_ids_by_option

    @classmethod
    def get_option_queryset(cls, request):
        queryset = Option.objects.select_related().prefetch_related(
            "options__items",
            Prefetch(
                "options",
                queryset=OptionItem.objects.select_related(
                    "item_name"
                ).order_by("id"),
            ),
        )

        if not request.user.is_staff:
            queryset = queryset.exclude(status=Option.STATUS_DRAFT)

        return queryset.order_by("id")
