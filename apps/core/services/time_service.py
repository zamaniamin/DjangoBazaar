from datetime import datetime


class DateTime:
    @classmethod
    def string(cls, obj: datetime):
        """Convert a datetime object to a formatted string."""

        return obj.strftime("%Y-%m-%d %H:%M:%S") if obj else None
