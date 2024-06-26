from faker import Faker

from apps.shop.models.review import Review


class ReviewFactory:
    faker = Faker()
    review_message_1 = "message 1"
    review_message_2 = "message 2"

    @classmethod
    def create_review(cls, review_message=""):
        if review_message:
            return Review.objects.create(message="message1")
        return Review.objects.create(message=cls.review_message_1)

    @classmethod
    def create_review_list(cls):
        Review.objects.create(message=cls.review_message_1)
        Review.objects.create(message=cls.review_message_2)
