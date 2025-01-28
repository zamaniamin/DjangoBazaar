import os
import re

from rest_framework.test import APITestCase

from config import settings


class ImageTestCaseMixin(APITestCase):
    def assertImageSrcPattern(self, src):
        # Define the regex pattern for the src
        pattern = r"^http://.*media.*$"

        # Assert that the src matches the pattern
        self.assertTrue(
            re.match(pattern, src), f"src '{src}' does not match the expected pattern"
        )

    def assertImageFileDirectory(self, src):
        """Assert that the image file exists in the correct directory based on the src URL."""

        # Extract the relative file path from the src
        match = re.search(r"testserver/(.*)", src)
        self.assertIsNotNone(match, "The src does not contain a valid path.")

        # Build the full path based on the extracted path and the base directory
        relative_path = match.group(1)
        full_file_path = os.path.join(settings.BASE_DIR, relative_path)

        # Assert that the file exists at the generated full path
        self.assertTrue(
            os.path.exists(full_file_path), f"File does not exist: {full_file_path}"
        )
