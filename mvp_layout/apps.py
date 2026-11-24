"""App configuration for django-mvp-layout."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MvpLayoutConfig(AppConfig):
    """What a project gets when it adds this package to INSTALLED_APPS.

    The label is set explicitly rather than left to Django's default, which is
    the last segment of the module path. Two installed apps whose paths end in
    the same word collide on that default, and the error names neither of them
    clearly.
    """

    name = "mvp_layout"
    label = "mvp_layout"
    verbose_name = _("Layout")
    default_auto_field = "django.db.models.BigAutoField"
