from datetime import datetime


class DateTime:

    @classmethod
    def string(cls, obj: datetime):
        """
        Convert a datetime object to a formatted string.

        Args:
            obj (datetime or None): The datetime object to be converted to a string.

        Returns: str or None: A formatted string representation of the datetime object, or None if the input is None
        or evaluates to False.

        """

        return obj.strftime('%Y-%m-%d %H:%M:%S') if obj else None
