from django.db import models
from django.utils.translation import gettext_lazy as _


class Salutation(models.TextChoices):
    MR = "mr", _("Mr.")
    MS = "ms", _("Ms.")
    MX = "mx", _("Mx.")
    UNSPECIFIED = "unspecified", _("Unspecified")


class Gender(models.TextChoices):
    FEMALE = "female", _("Female")
    MALE = "male", _("Male")
    DIVERSE = "diverse", _("Diverse")
    UNDISCLOSED = "undisclosed", _("Undisclosed")
