import os

from django.core.exceptions import ValidationError


def allow_only_images_validator(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = [".png", ".jpg", ".jpeg"]

    if not ext.lower() in valid_extensions:
        raise ValidationError(
            f"File type not supported, only {', '.join(valid_extensions)} are supported."
        )
