import os
import sys
import uuid

from django.db import models

from apps.core.models.mixin import ModelMixin


def generate_upload_path(instance, filename):
    """Generate dynamic upload path based on the related model"""
    unique_id = uuid.uuid4().hex
    _, ext = os.path.splitext(filename)
    folder = instance.get_related_folder()

    if "test" in sys.argv:
        return f"test/{folder}/{instance.get_related_id()}/{unique_id}{ext}"
    return f"{folder}/{instance.get_related_id()}/{unique_id}{ext}"


class AbstractImage(ModelMixin):
    # name = models.CharField(max_length=500, blank=True, null=True)
    src = models.ImageField(upload_to=generate_upload_path, blank=True, null=True)
    alt = models.CharField(max_length=500, blank=True, null=True)

    # size = models.PositiveIntegerField(
    #     default=0, blank=True, null=True
    # )  # Size in bytes
    # type = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        abstract = True

    def get_related_id(self):
        """Subclasses must implement to return related object ID"""
        raise NotImplementedError("Subclasses must implement `get_related_id`")

    def get_related_folder(self):
        """Subclasses must implement to return the folder name"""
        raise NotImplementedError("Subclasses must implement `get_related_folder`")
