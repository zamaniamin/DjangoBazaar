from datetime import datetime

from apps.core.services.time_service import DateTime


class TimeTestCase:

    @staticmethod
    def assertDatetimeFormat(date: str | datetime):
        if isinstance(date, datetime):
            date = DateTime.string(date)

        formatted_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
        assert date == formatted_date

    @staticmethod
    def convert_datetime_to_string(date):
        return DateTime.string(date)

    # def assertDatetimeFormat(self, date):
    #     formatted_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
    #     self.assertEqual(date, formatted_date)
