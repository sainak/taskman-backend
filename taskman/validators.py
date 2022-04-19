import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def avatar_validator(value):
    if not value.startswith("https://avatars.dicebear.com/api/"):
        raise ValidationError(
            _("Enter a valid DiceBear avatar url"),
            "invalid",
        )
